from typing import List

import numpy as np
from numpy.typing import ArrayLike
from pydub import AudioSegment


def __concatenate_with_silence(audios: List[ArrayLike], silence=0.5, sample_rate=22050):
    synth_audios = audios.copy()
    if silence > 0:
        silent_frames = np.array(
            AudioSegment.silent(duration=silence * 1000, frame_rate=sample_rate).get_array_of_samples(),
            dtype=np.float32)
        for i in reversed(range(len(synth_audios))[1:]):
            synth_audios.insert(i, silent_frames)

    return np.concatenate(tuple(synth_audios))


def concat_2d_array_audios_with_silence(audios: List[List[ArrayLike]], silence_between_dim1=1.0, silence_between_dim2=2.0, sr=22050):
    concatenated_sentences = [__concatenate_with_silence(book_audio, silence_between_dim1, sample_rate=sr)
                              for book_audio in audios if book_audio]

    return __concatenate_with_silence(concatenated_sentences, silence_between_dim2, sample_rate=sr)
