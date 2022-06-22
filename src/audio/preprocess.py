import os

import numpy as np
import torch
from scipy.io.wavfile import read

from src.mel_processing import spectrogram_torch


def load_wav_to_torch(full_path):
    sampling_rate, data = read(full_path)
    return torch.FloatTensor(data.astype(np.float32)), sampling_rate


def preprocess_audio(filename, target_sr, max_wav_value, filter_length, hop_length, win_length):
    audio, file_sr = load_wav_to_torch(filename)
    if file_sr != target_sr:
        raise ValueError(f"{file_sr} SR doesn't match target {target_sr} SR")

    audio_norm = audio / max_wav_value
    audio_norm = audio_norm.unsqueeze(0)
    spec_filename = filename.replace(".wav", ".spec.pt")

    if os.path.exists(spec_filename):
        spec = torch.load(spec_filename)
    else:
        spec = spectrogram_torch(audio_norm, filter_length, target_sr, hop_length, win_length, center=False)
        spec = torch.squeeze(spec, 0)
        torch.save(spec, spec_filename)

    return spec, audio_norm
