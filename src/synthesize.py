import time
from typing import List

import IPython.display as ipd
import librosa
import torch
from numpy import ndarray
from tqdm import tqdm

from src.logger import get_logger
from src.text.convert import preprocess_text
from src.text.symbols import get_vocabulary

logger = get_logger(__name__)


def __inference(sentence, net_g, hps, device=0):
    _, symbol_to_id, _ = get_vocabulary(hps.data.language)
    stn_tst = preprocess_text(sentence, hps.data.text_cleaners, symbol_to_id, add_blank=hps.data.add_blank)
    with torch.no_grad():
        x_tst = stn_tst.cuda(device).unsqueeze(0)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda(torch.device(device))
        return net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=0.9)[0][
            0, 0].data.cpu().float().numpy()


def synthesize(sentence, net_g, hps, device=0, speed: float = None, display_audio=True, log=True) -> ndarray:
    if log:
        logger.info(f"Synthesizing {sentence}")
    start_time = time.time()
    audio = __inference(sentence, net_g, hps, device)
    if log:
        logger.info(f"Synthesis duration: {time.time() - start_time}")

    if speed:
        # audio = pyrb.time_stretch(audio, hps.data.sample_rate, speed)
        audio = librosa.effects.time_stretch(audio, speed)

    if display_audio:
        ipd.display(ipd.Audio(audio, rate=hps.data.sample_rate, normalize=False))

    return audio
    # if output_dir:
    #     filename = normalize_sentence_to_filename(sentence)
    #     write(f"{output_dir}/{filename}.wav", 22050, audio)
    # else:
    #     return audio


def synthesize_all(sentences, net_g, hps, device=0, speed: int = None, display_audio=True, log=True) -> List[ndarray]:
    return [synthesize(sentence, net_g, hps, device=device, speed=speed, display_audio=display_audio, log=log)
            for sentence in tqdm(sentences)]


def synthesize_book(book_sentences, net_g, hps, device=0, speed: int = None):
    return [
        [synthesize(sentence, net_g, hps, device=device, speed=speed, display_audio=False, log=False)
         for sentence in sentences if sentence]
        for sentences in tqdm(book_sentences)
    ]
