from typing import List

import numpy as np
from numpy import ndarray
from pydub import AudioSegment


def concatenate_with_silence(audios: List[ndarray], silence=0.5):
    synth_audios = audios.copy()
    if silence > 0:
        silent_frames = np.array(AudioSegment.silent(duration=1000).get_array_of_samples(), dtype=np.float32)
        for i in reversed(range(len(synth_audios) - 1)):
            synth_audios.insert(i, silent_frames)

    return np.concatenate(tuple(synth_audios))


def concatenate_book_audios_with_silence(book_audios: List[List[ndarray]], sentence_silence=1.0, paragraph_silence=2.0):
    concatenated_sentences = [concatenate_with_silence(book_audio, sentence_silence) for book_audio in book_audios if book_audio]
    return concatenate_with_silence(concatenated_sentences, paragraph_silence)
