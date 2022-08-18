import math

import torch
from torch import nn
from torch.nn import Conv1d, Conv2d
from torch.nn import functional as F
from torch.nn.utils import weight_norm, spectral_norm

import commons
import modules
import monotonic_align
from commons import get_padding
from duration_predictor import DurationPredictor
from generator import Generator
from posterior_encoder import PosteriorEncoder
from residual_coupling_block import ResidualCouplingBlock
from stochastic_duration_predictor import StochasticDurationPredictor
from text_encoder import TextEncoder


class DiscriminatorP(torch.nn.Module):
  def __init__(self, period, kernel_size=5, stride=3, use_spectral_norm=False):
    super(DiscriminatorP, self).__init__()
    self.period = period
    self.use_spectral_norm = use_spectral_norm
    norm_f = weight_norm if use_spectral_norm == False else spectral_norm
    self.convs = nn.ModuleList([
      norm_f(Conv2d(1, 32, (kernel_size, 1), (stride, 1), padding=(get_padding(kernel_size, 1), 0))),
      norm_f(Conv2d(32, 128, (kernel_size, 1), (stride, 1), padding=(get_padding(kernel_size, 1), 0))),
      norm_f(Conv2d(128, 512, (kernel_size, 1), (stride, 1), padding=(get_padding(kernel_size, 1), 0))),
      norm_f(Conv2d(512, 1024, (kernel_size, 1), (stride, 1), padding=(get_padding(kernel_size, 1), 0))),
      norm_f(Conv2d(1024, 1024, (kernel_size, 1), 1, padding=(get_padding(kernel_size, 1), 0))),
    ])
    self.conv_post = norm_f(Conv2d(1024, 1, (3, 1), 1, padding=(1, 0)))

  def forward(self, x):
    fmap = []

    # 1d to 2d
    b, c, t = x.shape
    if t % self.period != 0:  # pad first
      n_pad = self.period - (t % self.period)
      x = F.pad(x, (0, n_pad), "reflect")
      t = t + n_pad
    x = x.view(b, c, t // self.period, self.period)

    for l in self.convs:
      x = l(x)
      x = F.leaky_relu(x, modules.LRELU_SLOPE)
      fmap.append(x)
    x = self.conv_post(x)
    fmap.append(x)
    x = torch.flatten(x, 1, -1)

    return x, fmap


class DiscriminatorS(torch.nn.Module):
  def __init__(self, use_spectral_norm=False):
    super(DiscriminatorS, self).__init__()
    norm_f = weight_norm if use_spectral_norm == False else spectral_norm
    self.convs = nn.ModuleList([
      norm_f(Conv1d(1, 16, 15, 1, padding=7)),
      norm_f(Conv1d(16, 64, 41, 4, groups=4, padding=20)),
      norm_f(Conv1d(64, 256, 41, 4, groups=16, padding=20)),
      norm_f(Conv1d(256, 1024, 41, 4, groups=64, padding=20)),
      norm_f(Conv1d(1024, 1024, 41, 4, groups=256, padding=20)),
      norm_f(Conv1d(1024, 1024, 5, 1, padding=2)),
    ])
    self.conv_post = norm_f(Conv1d(1024, 1, 3, 1, padding=1))

  def forward(self, x):
    fmap = []

    for l in self.convs:
      x = l(x)
      x = F.leaky_relu(x, modules.LRELU_SLOPE)
      fmap.append(x)
    x = self.conv_post(x)
    fmap.append(x)
    x = torch.flatten(x, 1, -1)

    return x, fmap


class MultiPeriodDiscriminator(torch.nn.Module):
  def __init__(self, use_spectral_norm=False):
    super(MultiPeriodDiscriminator, self).__init__()
    periods = [2, 3, 5, 7, 11]

    discs = [DiscriminatorS(use_spectral_norm=use_spectral_norm)]
    discs = discs + [DiscriminatorP(i, use_spectral_norm=use_spectral_norm) for i in periods]
    self.discriminators = nn.ModuleList(discs)

  def forward(self, y, y_hat):
    y_d_rs = []
    y_d_gs = []
    fmap_rs = []
    fmap_gs = []
    for i, d in enumerate(self.discriminators):
      y_d_r, fmap_r = d(y)
      y_d_g, fmap_g = d(y_hat)
      y_d_rs.append(y_d_r)
      y_d_gs.append(y_d_g)
      fmap_rs.append(fmap_r)
      fmap_gs.append(fmap_g)

    return y_d_rs, y_d_gs, fmap_rs, fmap_gs


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
    self.dec = Generator(inter_channels, resblock, resblock_kernel_sizes, resblock_dilation_sizes, upsample_rates, upsample_initial_channel, upsample_kernel_sizes, gin_channels=gin_channels)
    self.enc_q = PosteriorEncoder(spec_channels, inter_channels, hidden_channels, 5, 1, 16, gin_channels=gin_channels)
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
      neg_cent2 = torch.matmul(-0.5 * (z_p ** 2).transpose(1, 2), s_p_sq_r)  # [b, t_t, d] x [b, d, t_s] = [b, t_t, t_s]
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
    logs_p = torch.matmul(attn.squeeze(1), logs_p.transpose(1, 2)).transpose(1, 2)  # [b, t', t], [b, t, d] -> [b, d, t']

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
