import torch

from hparams import get_hparams_from_file
from inference import SynthesizerInf
from load_checkpoint import load_checkpoint
from symbols import symbols
from to_wave import write

# ----------------------------------------------------------------------------------------------------------------------

_symbol_to_id = {s: i for i, s in enumerate(symbols)}


def get_text(text, hps):
  text_norm = [_symbol_to_id[symbol] for symbol in text if symbol in _symbol_to_id.keys()]
  if hps.data.add_blank:
    result = [0] * (len(text_norm) * 2 + 1)
    result[1::2] = text_norm
    text_norm = result
  text_norm = torch.LongTensor(text_norm)
  return text_norm


# ----------------------------------------------------------------------------------------------------------------------

def pt(cfg, cleaned):
  hps = get_hparams_from_file(cfg.Config)

  model = torch.jit.load(cfg.Model).eval()
  torch.set_grad_enabled(False)

  stn_tst = get_text(cleaned, hps)
  raw = model(stn_tst.unsqueeze(0), torch.LongTensor([stn_tst.size(0)]))[0][0, 0].data.float().numpy()
  return write(cfg.Output, hps.data.sampling_rate, raw)


# ----------------------------------------------------------------------------------------------------------------------

def pth(cfg, cleaned):
  hps = get_hparams_from_file(cfg.Config)
  model = SynthesizerInf(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model).eval()

  _ = load_checkpoint(cfg.Model, model, None)
  torch.set_grad_enabled(False)

  stn_tst = get_text(cleaned, hps)
  raw = model.forward(stn_tst.unsqueeze(0), torch.LongTensor([stn_tst.size(0)]), cfg.Scale)[0][
    0, 0].data.float().numpy()
  return write(cfg.Output, hps.data.sampling_rate, raw)
