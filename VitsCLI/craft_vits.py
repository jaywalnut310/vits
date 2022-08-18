import torch

from hparams import get_hparams_from_file
from inference import SynthesizerInf
from load_checkpoint import load_checkpoint
from symbols import symbols

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

def pt_do(cfg_path, pt_path, cleaned):
  hps = get_hparams_from_file(cfg_path)

  model = torch.jit.load(pt_path).eval()
  torch.set_grad_enabled(False)

  stn_tst = get_text(cleaned, hps)
  return model(stn_tst.unsqueeze(0), torch.LongTensor([stn_tst.size(0)]))[0][0, 0].data.float().numpy().tobytes()


# ----------------------------------------------------------------------------------------------------------------------

def pth_do(cfg_path, pt_path, cleaned, length_scale=1):
  hps = get_hparams_from_file(cfg_path)
  model = SynthesizerInf(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model).eval()

  _ = load_checkpoint(pt_path, model, None)
  torch.set_grad_enabled(False)

  stn_tst = get_text(cleaned, hps)
  return model.forward(stn_tst.unsqueeze(0), torch.LongTensor([stn_tst.size(0)]), length_scale=length_scale)[0][
    0, 0].data.float().numpy().tobytes()
