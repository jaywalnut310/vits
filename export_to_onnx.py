from onnx_export.onnx_models import SynthesizerTrn
import utils
from text import text_to_sequence
from text.symbols import symbols
import torch
import commons

export_path = "onnx_export"

def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm

hps = utils.get_hparams_from_file("config.json")

net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    n_speakers=hps.data.n_speakers,
    **hps.model)
_ = net_g.eval()
_ = utils.load_checkpoint("G_76000.pth", net_g)

stn_tst = get_text("onnx test.", hps)
with torch.no_grad():
    x_tst = stn_tst.unsqueeze(0)
    x_tst_lengths = torch.LongTensor([stn_tst.size(0)])
    if hps.data.n_speakers > 0:
        sid = torch.tensor([0])
    else:
        sid = None
    net_g(x_tst, x_tst_lengths, sid, export_path)