import math
import time
from pathlib import Path
from typing import List

import IPython.display as ipd
import torch
from scipy.io.wavfile import write
from torch import nn

import monotonic_align
from hparams import get_hparams_from_file
from src.core import SynthesizedUtterance
from src.logger import get_logger
from src.model import commons
from src.model.checkpoint import load_checkpoint
from src.model.encoders import TextEncoder, PosteriorEncoder
from src.model.generators import Generator
from src.model.modules import ResidualCouplingBlock
from src.model.predictors import StochasticDurationPredictor, DurationPredictor
from src.plot import plot_alignment
from src.text.convert import preprocess_text
from src.text.symbols import get_vocabulary

logger = get_logger(__name__)


class SynthesizerTrn(nn.Module):
    """
    Synthesizer for Training
    """

    def __init__(self,
                 n_vocab,
                 spec_channels,
                 segment_size,
                 inter_channels,
                 hidden_channels,
                 filter_channels,
                 n_heads,
                 n_layers,
                 kernel_size,
                 p_dropout,
                 resblock,
                 resblock_kernel_sizes,
                 resblock_dilation_sizes,
                 upsample_rates,
                 upsample_initial_channel,
                 upsample_kernel_sizes,
                 n_speakers=0,
                 gin_channels=0,
                 use_sdp=True,
                 **kwargs):

        super().__init__()
        self.n_vocab = n_vocab
        self.spec_channels = spec_channels
        self.inter_channels = inter_channels
        self.hidden_channels = hidden_channels
        self.filter_channels = filter_channels
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.kernel_size = kernel_size
        self.p_dropout = p_dropout
        self.resblock = resblock
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.upsample_rates = upsample_rates
        self.upsample_initial_channel = upsample_initial_channel
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.segment_size = segment_size
        self.n_speakers = n_speakers
        self.gin_channels = gin_channels

        self.use_sdp = use_sdp

        self.enc_p = TextEncoder(n_vocab,
                                 inter_channels,
                                 hidden_channels,
                                 filter_channels,
                                 n_heads,
                                 n_layers,
                                 kernel_size,
                                 p_dropout)
        self.dec = Generator(inter_channels, resblock, resblock_kernel_sizes, resblock_dilation_sizes, upsample_rates,
                             upsample_initial_channel, upsample_kernel_sizes, gin_channels=gin_channels)
        self.enc_q = PosteriorEncoder(spec_channels, inter_channels, hidden_channels, 5, 1, 16,
                                      gin_channels=gin_channels)
        self.flow = ResidualCouplingBlock(inter_channels, hidden_channels, 5, 1, 4, gin_channels=gin_channels)

        if use_sdp:
            self.dp = StochasticDurationPredictor(hidden_channels, 192, 3, 0.5, 4, gin_channels=gin_channels)
        else:
            self.dp = DurationPredictor(hidden_channels, 256, 3, 0.5, gin_channels=gin_channels)

        if n_speakers > 1:
            self.emb_g = nn.Embedding(n_speakers, gin_channels)

    def forward(self, x, x_lengths, y, y_lengths, sid=None):

        x, m_p, logs_p, x_mask = self.enc_p(x, x_lengths)
        if self.n_speakers > 0:
            g = self.emb_g(sid).unsqueeze(-1)  # [b, h, 1]
        else:
            g = None

        z, m_q, logs_q, y_mask = self.enc_q(y, y_lengths, g=g)
        z_p = self.flow(z, y_mask, g=g)

        with torch.no_grad():
            # negative cross-entropy
            s_p_sq_r = torch.exp(-2 * logs_p)  # [b, d, t]
            neg_cent1 = torch.sum(-0.5 * math.log(2 * math.pi) - logs_p, [1], keepdim=True)  # [b, 1, t_s]
            neg_cent2 = torch.matmul(-0.5 * (z_p ** 2).transpose(1, 2),
                                     s_p_sq_r)  # [b, t_t, d] x [b, d, t_s] = [b, t_t, t_s]
            neg_cent3 = torch.matmul(z_p.transpose(1, 2), (m_p * s_p_sq_r))  # [b, t_t, d] x [b, d, t_s] = [b, t_t, t_s]
            neg_cent4 = torch.sum(-0.5 * (m_p ** 2) * s_p_sq_r, [1], keepdim=True)  # [b, 1, t_s]
            neg_cent = neg_cent1 + neg_cent2 + neg_cent3 + neg_cent4

            attn_mask = torch.unsqueeze(x_mask, 2) * torch.unsqueeze(y_mask, -1)
            attn = monotonic_align.maximum_path(neg_cent, attn_mask.squeeze(1)).unsqueeze(1).detach()

        w = attn.sum(2)
        if self.use_sdp:
            l_length = self.dp(x, x_mask, w, g=g)
            l_length = l_length / torch.sum(x_mask)
        else:
            logw_ = torch.log(w + 1e-6) * x_mask
            logw = self.dp(x, x_mask, g=g)
            l_length = torch.sum((logw - logw_) ** 2, [1, 2]) / torch.sum(x_mask)  # for averaging

        # expand prior
        m_p = torch.matmul(attn.squeeze(1), m_p.transpose(1, 2)).transpose(1, 2)
        logs_p = torch.matmul(attn.squeeze(1), logs_p.transpose(1, 2)).transpose(1, 2)

        z_slice, ids_slice = commons.rand_slice_segments(z, y_lengths, self.segment_size)
        o = self.dec(z_slice, g=g)
        return o, l_length, attn, ids_slice, x_mask, y_mask, (z, z_p, m_p, logs_p, m_q, logs_q)

    def infer(self, x, x_lengths, sid=None, noise_scale=1, length_scale=1, noise_scale_w=1., max_len=None):
        x, m_p, logs_p, x_mask = self.enc_p(x, x_lengths)
        if self.n_speakers > 0:
            g = self.emb_g(sid).unsqueeze(-1)  # [b, h, 1]
        else:
            g = None

        if self.use_sdp:
            logw = self.dp(x, x_mask, g=g, reverse=True, noise_scale=noise_scale_w)
        else:
            logw = self.dp(x, x_mask, g=g)
        w = torch.exp(logw) * x_mask * length_scale
        w_ceil = torch.ceil(w)
        y_lengths = torch.clamp_min(torch.sum(w_ceil, [1, 2]), 1).long()
        y_mask = torch.unsqueeze(commons.sequence_mask(y_lengths, None), 1).to(x_mask.dtype)
        attn_mask = torch.unsqueeze(x_mask, 2) * torch.unsqueeze(y_mask, -1)
        attn = commons.generate_path(w_ceil, attn_mask)

        m_p = torch.matmul(attn.squeeze(1), m_p.transpose(1, 2)).transpose(1, 2)  # [b, t', t], [b, t, d] -> [b, d, t']
        logs_p = torch.matmul(attn.squeeze(1), logs_p.transpose(1, 2)).transpose(1,
                                                                                 2)  # [b, t', t], [b, t, d] -> [b, d, t']

        z_p = m_p + torch.randn_like(m_p) * torch.exp(logs_p) * noise_scale
        z = self.flow(z_p, y_mask, g=g, reverse=True)
        o = self.dec((z * y_mask)[:, :, :max_len], g=g)
        return o, attn, y_mask, (z, z_p, m_p, logs_p)

    def voice_conversion(self, y, y_lengths, sid_src, sid_tgt):
        assert self.n_speakers > 0, "n_speakers have to be larger than 0."
        g_src = self.emb_g(sid_src).unsqueeze(-1)
        g_tgt = self.emb_g(sid_tgt).unsqueeze(-1)
        z, m_q, logs_q, y_mask = self.enc_q(y, y_lengths, g=g_src)
        z_p = self.flow(z, y_mask, g=g_src)
        z_hat = self.flow(z_p, y_mask, g=g_tgt, reverse=True)
        o_hat = self.dec(z_hat * y_mask, g=g_tgt)
        return o_hat, y_mask, (z, z_p, z_hat)


class Synthesizer:
    def __init__(self, hps, checkpoint_path, device=0):
        self.text_cleaners = hps.data.text_cleaners
        self.sample_rate = hps.data.sample_rate
        self.add_blank = hps.data.add_blank
        self.device = device
        self.symbols, self.symbol_to_id, _ = get_vocabulary(hps.data.language)
        self.net_g = self.__setup_synthesis_model(hps, checkpoint_path)

    def synthesize(self, text, verbose=False, show_player=False, plot_align=False,
                   output_dir=None) -> SynthesizedUtterance:
        if len(text) == 0:
            raise ValueError("Cannot synthesize empty text.")

        if verbose:
            logger.info(f"Synthesizing {text}")

        text_tensor = preprocess_text(text, self.text_cleaners, self.symbol_to_id, add_blank=self.add_blank)
        start_time = time.time()
        with torch.no_grad():
            x = text_tensor.unsqueeze(0).cuda(self.device)
            x_lengths = torch.LongTensor([text_tensor.size(0)]).cuda(torch.device(self.device))

            y_hat, attn, _, _ = self.net_g.infer(x, x_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=1)

            audio = y_hat[0, 0].data.cpu().float().numpy()

        if verbose:
            logger.info("Synthesis duration:", time.time() - start_time)

        utterance = SynthesizedUtterance.from_text_and_audio(text, audio, self.sample_rate)

        if show_player:
            ipd.display(ipd.Audio(utterance.audio, rate=self.sample_rate, normalize=False))

        if output_dir:
            write(f"{output_dir}/{utterance.filename}.wav", self.sample_rate, audio)

            if plot_align:
                plot_alignment(attn[0, 0].data.cpu().numpy(),
                               imshow=False,
                               out_filepath=f"{output_dir}/{utterance.filename}.png")

        return utterance

    def synthesize_all(self, text_list, verbose=False, show_player=False, plot_align=False, output_dir=None):
        for text in text_list:
            self.synthesize(text, verbose, show_player, plot_align, output_dir)

        logger.info(f"Synthesized {len(text_list)} utterances.")

    def __setup_synthesis_model(self, hps, path):
        net_g = SynthesizerTrn(
            len(self.symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            **hps.model).cuda(self.device)
        net_g.eval()
        net_g, _, _, _ = load_checkpoint(hps.train, path, net_g)
        return net_g


class InferenceConfig:
    synthesizer: Synthesizer
    stressed: bool
    output_dir: Path = None

    def __init__(self, config_name, checkpoint_step: int, speaker: str, stressed: bool, device: int = 0):
        self.stressed = stressed
        self.checkpoint_path = Path(
            f"/home/aai-labs/inovoice/models/{speaker}/G_{checkpoint_step}.pth")
        self.output_dir = Path(
            f"/home/aai-labs/inovoice/repos/vits/files/audio/samples/{speaker}/{checkpoint_step}")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        hps = get_hparams_from_file(f"/home/aai-labs/inovoice/repos/vits/files/configs/{config_name}.json")
        self.synthesizer = Synthesizer(hps, self.checkpoint_path, device=device)
