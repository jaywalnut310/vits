import torch

import commons
from text.symbols import symbols

_symbol_to_id = {s: i for i, s in enumerate(symbols)}


def get_text(text, hps):
  text_norm = [_symbol_to_id[symbol] for symbol in text if symbol in _symbol_to_id.keys()]
  if hps.data.add_blank:
    text_norm = commons.intersperse(text_norm, 0)
  text_norm = torch.LongTensor(text_norm)
  return text_norm
