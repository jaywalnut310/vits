import copy
import math
import torch
from torch import nn
from torch.nn import functional as F

import commons
import onnx_export.onnx_modules as modules
import attentions

from torch.nn import Conv1d, ConvTranspose1d, AvgPool1d, Conv2d
from torch.nn.utils import weight_norm, remove_weight_norm, spectral_norm
from commons import init_weights, get_padding


class StochasticDurationPredictor(nn.Module):
  def __init__(self, in_channels, filter_channels, kernel_size, p_dropout, n_flows=4, gin_channels=0):
    super().__init__()
    filter_channels = in_channels # it needs to be removed from future version.
    self.in_channels = in_channels
    self.filter_channels = filter_channels
    self.kernel_size = kernel_size
    self.p_dropout = p_dropout
    self.n_flows = n_flows
    self.gin_channels = gin_channels

    self.log_flow = modules.Log()
    self.flows = nn.ModuleList()
    self.flows.append(modules.ElementwiseAffine(2))
    for i in range(n_flows):
      self.flows.append(modules.ConvFlow(2, filter_channels, kernel_size, n_layers=3))
      self.flows.append(modules.Flip())

    self.post_pre = nn.Conv1d(1, filter_channels, 1)
    self.post_proj = nn.Conv1d(filter_channels, filter_channels, 1)
    self.post_convs = modules.DDSConv(filter_channels, kernel_size, n_layers=3, p_dropout=p_dropout)
    self.post_flows = nn.ModuleList()
    self.post_flows.append(modules.ElementwiseAffine(2))
    for i in range(4):
      self.post_flows.append(modules.ConvFlow(2, filter_channels, kernel_size, n_layers=3))
      self.post_flows.append(modules.Flip())

    self.pre = nn.Conv1d(in_channels, filter_channels, 1)
    self.proj = nn.Conv1d(filter_channels, filter_channels, 1)
    self.convs = modules.DDSConv(filter_channels, kernel_size, n_layers=3, p_dropout=p_dropout)
    if gin_channels != 0:
      self.cond = nn.Conv1d(gin_channels, filter_channels, 1)

    self.w = None
    self.reverse = None
    self.noise_scale = None
  def forward(self, x, x_mask, zin, g=None):
    w = self.w
    reverse = self.reverse
    noise_scale = self.noise_scale

    x = torch.detach(x)
    x = self.pre(x)
    if g is not None:
      g = torch.detach(g)
      x = x + self.cond(g)
    x = self.convs(x, x_mask)
    x = self.proj(x) * x_mask

    flows = list(reversed(self.flows))
    flows = flows[:-2] + [flows[-1]] # remove a useless vflow
    z = zin
    for flow in flows:
      z = flow(z, x_mask, g=x, reverse=reverse)
    z0, z1 = torch.split(z, [1, 1], 1)
    logw = z0
    return logw


class TextEncoder(nn.Module):
  def __init__(self,
      n_vocab,
      out_channels,
      hidden_channels,
      filter_channels,
      n_heads,
      n_layers,
      kernel_size,
      p_dropout):
    super().__init__()
    self.n_vocab = n_vocab
    self.out_channels = out_channels
    self.hidden_channels = hidden_channels
    self.filter_channels = filter_channels
    self.n_heads = n_heads
    self.n_layers = n_layers
    self.kernel_size = kernel_size
    self.p_dropout = p_dropout

    self.emb = nn.Embedding(n_vocab, hidden_channels)
    nn.init.normal_(self.emb.weight, 0.0, hidden_channels**-0.5)

    self.encoder = attentions.Encoder(
      hidden_channels,
      filter_channels,
      n_heads,
      n_layers,
      kernel_size,
      p_dropout)
    self.proj= nn.Conv1d(hidden_channels, out_channels * 2, 1)

  def forward(self, x, x_lengths):
    x = self.emb(x) * math.sqrt(self.hidden_channels) # [b, t, h]
    x = torch.transpose(x, 1, -1) # [b, h, t]
    x_mask = torch.unsqueeze(commons.sequence_mask(x_lengths, x.size(2)), 1).to(x.dtype)

    x = self.encoder(x * x_mask, x_mask)
    stats = self.proj(x) * x_mask

    m, logs = torch.split(stats, self.out_channels, dim=1)
    return x, m, logs, x_mask


class ResidualCouplingBlock(nn.Module):
  def __init__(self,
      channels,
      hidden_channels,
      kernel_size,
      dilation_rate,
      n_layers,
      n_flows=4,
      gin_channels=0):
    super().__init__()
    self.channels = channels
    self.hidden_channels = hidden_channels
    self.kernel_size = kernel_size
    self.dilation_rate = dilation_rate
    self.n_layers = n_layers
    self.n_flows = n_flows
    self.gin_channels = gin_channels

    self.flows = nn.ModuleList()
    for i in range(n_flows):
      self.flows.append(modules.ResidualCouplingLayer(channels, hidden_channels, kernel_size, dilation_rate, n_layers, gin_channels=gin_channels, mean_only=True))
      self.flows.append(modules.Flip())

    self.reverse = None
  def forward(self, x, x_mask, g=None):
    reverse = self.reverse 
    if not reverse:
      for flow in self.flows:
        x, _ = flow(x, x_mask, g=g, reverse=reverse)
    else:
      for flow in reversed(self.flows):
        x = flow(x, x_mask, g=g, reverse=reverse)
    return x


class PosteriorEncoder(nn.Module):
  def __init__(self,
      in_channels,
      out_channels,
      hidden_channels,
      kernel_size,
      dilation_rate,
      n_layers,
      gin_channels=0):
    super().__init__()
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.hidden_channels = hidden_channels
    self.kernel_size = kernel_size
    self.dilation_rate = dilation_rate
    self.n_layers = n_layers
    self.gin_channels = gin_channels

    self.pre = nn.Conv1d(in_channels, hidden_channels, 1)
    self.enc = modules.WN(hidden_channels, kernel_size, dilation_rate, n_layers, gin_channels=gin_channels)
    self.proj = nn.Conv1d(hidden_channels, out_channels * 2, 1)

  def forward(self, x, x_lengths, g=None):
    x_mask = torch.unsqueeze(commons.sequence_mask(x_lengths, x.size(2)), 1).to(x.dtype)
    x = self.pre(x) * x_mask # x_in : [b, c, t] -> [b, h, t] 
    x = self.enc(x, x_mask, g=g) # x_in : [b, h, t], g : [b, h, 1],  x = x_in + g
    stats = self.proj(x) * x_mask
    m, logs = torch.split(stats, self.out_channels, dim=1)
    z = (m + torch.randn_like(m) * torch.exp(logs)) * x_mask
    return z, m, logs, x_mask # z, m, logs : [b, h, t]


class Generator(torch.nn.Module):
    def __init__(self, initial_channel, resblock, resblock_kernel_sizes, resblock_dilation_sizes, upsample_rates, upsample_initial_channel, upsample_kernel_sizes, gin_channels=0):
        super(Generator, self).__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.num_upsamples = len(upsample_rates)
        self.conv_pre = Conv1d(initial_channel, upsample_initial_channel, 7, 1, padding=3)
        resblock = modules.ResBlock1 if resblock == '1' else modules.ResBlock2

        self.ups = nn.ModuleList()
        for i, (u, k) in enumerate(zip(upsample_rates, upsample_kernel_sizes)):
            self.ups.append(weight_norm(
                ConvTranspose1d(upsample_initial_channel//(2**i), upsample_initial_channel//(2**(i+1)),
                                k, u, padding=(k-u)//2)))

        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = upsample_initial_channel//(2**(i+1))
            for j, (k, d) in enumerate(zip(resblock_kernel_sizes, resblock_dilation_sizes)):
                self.resblocks.append(resblock(ch, k, d))

        self.conv_post = Conv1d(ch, 1, 7, 1, padding=3, bias=False)
        self.ups.apply(init_weights)

        if gin_channels != 0:
            self.cond = nn.Conv1d(gin_channels, upsample_initial_channel, 1)

    def forward(self, x, g=None):
        x = self.conv_pre(x)
        if g is not None:
          x = x + self.cond(g)

        for i in range(self.num_upsamples):
            x = F.leaky_relu(x, modules.LRELU_SLOPE)
            x = self.ups[i](x)
            xs = None
            for j in range(self.num_kernels):
                if xs is None:
                    xs = self.resblocks[i*self.num_kernels+j](x)
                else:
                    xs += self.resblocks[i*self.num_kernels+j](x)
            x = xs / self.num_kernels
        x = F.leaky_relu(x)
        x = self.conv_post(x)
        x = torch.tanh(x)

        return x

    def remove_weight_norm(self):
        print('Removing weight norm...')
        for l in self.ups:
            remove_weight_norm(l)
        for l in self.resblocks:
            l.remove_weight_norm()


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
        if t % self.period != 0: # pad first
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
        periods = [2,3,5,7,11]

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

    self.dp = StochasticDurationPredictor(hidden_channels, 192, 3, 0.5, 4, gin_channels=gin_channels)

    if n_speakers > 0:
      self.emb_g = nn.Embedding(n_speakers, gin_channels)

  def forward(self, x, x_lengths, sid=None, path=None):
    noise_scale=.667
    length_scale=1
    noise_scale_w=0.8
    max_len=None
    torch.onnx.export(
        self.enc_p,
        (x, x_lengths),
        f"{path}/enc_p.onnx",
        input_names=["x", "x_lengths"],
        output_names=["xout", "m_p", "logs_p", "x_mask"],
        dynamic_axes={
          "x" : [0,1],
          "xout" : [0,2],
          "m_p" : [0,2],
          "logs_p" : [0,2],
          "x_mask" : [0,2]
        },
        verbose=True,
    )
    x, m_p, logs_p, x_mask = self.enc_p(x, x_lengths)

    if self.n_speakers > 0:
      g = self.emb_g(sid).unsqueeze(-1) # [b, h, 1]
      torch.onnx.export(
            self.emb_g,
            (sid),
            f"{path}/emb.onnx",
            input_names=["sid"],
            output_names=["g"],
            verbose=True,
        )
    else:
      g = None
    zinput = torch.randn(x.size(0), 2, x.size(2)).to(device=x.device, dtype=x.dtype) * noise_scale_w
    self.dp.reverse = True
    self.dp.noise_scale = noise_scale_w
    torch.onnx.export(
        self.dp,
        (x, x_mask, zinput, g),
        f"{path}/dp.onnx",
        input_names=["x", "x_mask", "zin", "g"],
        output_names=["logw"],
        dynamic_axes={
          "x" : [0,2],
          "x_mask" : [0,2],
          "zin" : [0,2],
          "logw" : [0,2]
        },
        verbose=True,
    )
    logw = self.dp(x, x_mask, zinput, g=g)
    w = torch.exp(logw) * x_mask * length_scale
    w_ceil = torch.ceil(w)
    y_lengths = torch.clamp_min(torch.sum(w_ceil, [1, 2]), 1).long()
    y_mask = torch.unsqueeze(commons.sequence_mask(y_lengths, None), 1).to(x_mask.dtype)
    attn_mask = torch.unsqueeze(x_mask, 2) * torch.unsqueeze(y_mask, -1)
    attn = commons.generate_path(w_ceil, attn_mask)

    m_p = torch.matmul(attn.squeeze(1), m_p.transpose(1, 2)).transpose(1, 2) # [b, t', t], [b, t, d] -> [b, d, t']
    logs_p = torch.matmul(attn.squeeze(1), logs_p.transpose(1, 2)).transpose(1, 2) # [b, t', t], [b, t, d] -> [b, d, t']

    z_p = m_p + torch.randn_like(m_p) * torch.exp(logs_p) * noise_scale

    self.flow.reverse = True
    torch.onnx.export(
        self.flow,
        (z_p, y_mask, g),
        f"{path}/flow.onnx",
        input_names=["z_p", "y_mask", "g"],
        output_names=["z"],
        dynamic_axes={
          "z_p" : [0,2],
          "y_mask" : [0,2],
          "z" : [0,2]
        },
        verbose=True,
    )
    z = self.flow(z_p, y_mask, g=g)
    z_in = (z * y_mask)[:,:,:max_len]

    torch.onnx.export(
        self.dec,
        (z_in, g),
        f"{path}/dec.onnx",
        input_names=["z_in", "g"],
        output_names=["o"],
        dynamic_axes={
          "z_in" : [0,2],
          "o" : [0,2]
        },
        verbose=True,
    )
    o = self.dec(z_in, g=g)
    return o
