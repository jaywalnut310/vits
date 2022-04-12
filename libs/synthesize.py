import re
import time
import unicodedata
from typing import List

import IPython.display as ipd
import librosa
import torch
from numpy import ndarray
from scipy.io.wavfile import write
from tqdm import tqdm

import commons
from logger import get_logger
from text import text_to_sequence

logger = get_logger(__name__)


def __inference(sentence, net_g, hps):
    stn_tst = get_text(sentence, hps)
    with torch.no_grad():
        x_tst = stn_tst.cuda().unsqueeze(0)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
        return net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=1)[0][
            0, 0].data.cpu().float().numpy()


def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm


def normalize_sentence_to_filename(sentence):
    normalized_sentence = unicodedata.normalize('NFKD', sentence).encode('ascii', 'ignore').decode('utf-8')
    normalized_sentence = normalized_sentence.lower()
    normalized_sentence = re.sub(r'[^\w\s]', '', normalized_sentence)  # remove punctuation
    return '_'.join(normalized_sentence.split(' ')[:8])


def synthesize(sentence, net_g, hps, speed: float = None, output_dir=None, display_audio=True, log=True) -> ndarray:
    if log:
        logger.info(f"Synthesizing {sentence}")
    start_time = time.time()
    audio = __inference(sentence, net_g, hps)
    if log:
        logger.info(f"Synthesis duration: {time.time() - start_time}")

    if speed:
        # audio = pyrb.time_stretch(audio, hps.data.sampling_rate, speed)
        audio = librosa.effects.time_stretch(audio, speed)

    if display_audio:
        ipd.display(ipd.Audio(audio, rate=hps.data.sampling_rate, normalize=False))

    if output_dir:
        filename = normalize_sentence_to_filename(sentence)
        write(f"{output_dir}/{filename}.wav", 22050, audio)
    else:
        return audio


def synthesize_all(sentences, net_g, hps, speed: int = None, output_dir=None, display_audio=True, log=True) -> List[ndarray]:
    return [synthesize(sentence, net_g, hps, speed=speed, output_dir=output_dir, display_audio=display_audio, log=log)
            for sentence in tqdm(sentences)]


def synthesize_book(book_sentences, net_g, hps, speed: int = None):
    return [[synthesize(sentence, net_g, hps, speed=speed, display_audio=False, log=False) for sentence in sentences if sentence]
            for sentences in tqdm(book_sentences)]
