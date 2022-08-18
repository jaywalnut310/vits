import torch
from torch import nn
from torch.nn import Conv1d, ConvTranspose1d, functional as F
from torch.nn.utils import weight_norm, remove_weight_norm

import modules
from commons import init_weights


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
        ConvTranspose1d(upsample_initial_channel // (2 ** i), upsample_initial_channel // (2 ** (i + 1)),
                        k, u, padding=(k - u) // 2)))

    self.resblocks = nn.ModuleList()
    for i in range(len(self.ups)):
      ch = upsample_initial_channel // (2 ** (i + 1))
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
          xs = self.resblocks[i * self.num_kernels + j](x)
        else:
          xs += self.resblocks[i * self.num_kernels + j](x)
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
