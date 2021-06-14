import matplotlib.pyplot as plt

import os
import json
import math
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader

import commons
import utils
from data_utils import TextAudioLoader, TextAudioCollate, TextAudioSpeakerLoader, TextAudioSpeakerCollate
from models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence

from scipy.io.wavfile import write
import gradio as gr
import scipy.io.wavfile
import numpy as np
import torchtext

torchtext.utils.download_from_url("https://drive.google.com/uc?id=1q86w74Ygw2hNzYP9cWkeClGT5X25PvBT", root=".")


def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm

hps = utils.get_hparams_from_file("./configs/ljs_base.json")
net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model)
_ = net_g.eval()

_ = utils.load_checkpoint("pretrained_ljs.pth", net_g, None)
def inference(text):
    stn_tst = get_text(text, hps)
    with torch.no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)])
        audio = net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=1)[0][0,0].data.float().numpy()
        scipy.io.wavfile.write("out.wav", hps.data.sampling_rate, audio)
        return "./out.wav"


inputs = gr.inputs.Textbox(label="Input Text")
outputs =  gr.outputs.File(label="Output Audio")


title = "VITS"
description = "demo for VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech. To use it, simply upload your text, or click one of the examples to load them. Read more at the links below."
article = "<p style='text-align: center'><a href='https://arxiv.org/abs/2106.06103'>Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech</a> | <a href='https://github.com/jaywalnut310/vits'>Github Repo</a></p>"

gr.Interface(inference, inputs, outputs, title=title, description=description, article=article).launch(debug=True)
