from pathlib import Path
from typing import List

from numpy.typing import ArrayLike

from src.core import Sample, SrtEntry


def generate_and_save_audiobook_srt(audios: List[List[ArrayLike]], sentences: List[List[str]], sample_rate: int,
                                    fill_sentences: float, fill_paragraphs: float, out_filepath: Path):
    samples = audiobook_audios_and_sentences_to_samples(audios, sentences, sample_rate=sample_rate)
    srt_entries = srt_entries_from_audiobook_samples(samples, fill_sentences, fill_paragraphs)
    save_srt_entries_to_file(srt_entries, out_filepath)


def audiobook_audios_and_sentences_to_samples(audios: List[List[ArrayLike]], utterances: List[List[str]], sample_rate):
    return [[Sample(audio=audio, text=utterance, sample_rate=sample_rate) for audio, utterance in zip(a, u)]
            for (a, u) in zip(audios, utterances)]


def srt_entries_from_audiobook_samples(list_of_list_of_samples: List[List[Sample]], fill_sentences: float,
                                       fill_paragraphs: float) -> List[SrtEntry]:
    srt_entries: List[SrtEntry] = []
    curr_start = 0.0
    idx = 1
    for samples in list_of_list_of_samples:
        for sample in samples:
            duration = len(sample.audio) / sample.sample_rate
            end = curr_start + duration
            srt_entries.append(
                SrtEntry(idx=idx, start=curr_start * 1000, end=end * 1000, text=sample.text))
            idx += 1
            curr_start = end + fill_sentences
        curr_start += fill_paragraphs - fill_sentences
    return srt_entries


def save_srt_entries_to_file(srt_entries: List[SrtEntry], out_filepath: Path):
    text = '\n\n'.join([srt_entry.to_string() for srt_entry in srt_entries])
    with open(out_filepath, mode='w', encoding='utf-8') as f:
        f.write(text)
