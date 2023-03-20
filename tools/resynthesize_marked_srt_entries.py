import os
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List

from src.core import SrtPair, SrtEntry, SynthesizedUtterance
from src.logger import get_logger
from src.model.config import Speaker, get_inference_configs, InferenceConfig
from src.text.symbols import get_vocabulary

logger = get_logger(__name__)

vocabulary, _, _ = get_vocabulary('lt')


@dataclass
class MarkedSrtPair:
    srt_pair: SrtPair
    marked_entries: List[SrtEntry]

    def update(self, idx_in_full_srt: int, idx_in_marked_srt: int, utterance: SynthesizedUtterance):
        self.srt_pair.update_entry_by_utternace(idx_in_full_srt, utterance)
        self.__update_marked_entry(idx_in_marked_srt, utterance)

    def __update_marked_entry(self, idx: int, utterance: SynthesizedUtterance):
        old_entry = self.marked_entries[idx]
        offset = utterance.duration - (old_entry.end - old_entry.start)
        self.marked_entries[idx] = replace(old_entry,
                                           end=old_entry.end + offset,
                                           text=utterance.text,
                                           audio=utterance.audio_segment)

        for i, entry in enumerate(self.marked_entries[idx + 1:], start=idx + 1):
            self.marked_entries[i] = replace(entry, start=entry.start + offset, end=entry.end + offset)

    def save(self, output_directory: Path):
        self.srt_pair.save_pair(output_directory)
        self.__save_marked_srt(output_directory)

    def __save_marked_srt(self, output_directory: Path):
        out_filepath = output_directory / f"{self.srt_pair.filename}_marked.srt"
        logger.info(f"Saving marked SRT file to {out_filepath}")
        text = '\n\n'.join([srt_entry.to_string() for srt_entry in self.marked_entries])
        with open(out_filepath, mode='w', encoding='utf-8') as f:
            f.write(text)


def log_filename(srt_pair: SrtPair) -> SrtPair:
    logger.info(f"Resynthesizing entries in file {srt_pair.filename}")
    return srt_pair


def filter_marked_entries(srt_pair: SrtPair) -> MarkedSrtPair:
    marked_entries = [entry for entry in srt_pair.entries if '*' in entry.text]
    return MarkedSrtPair(srt_pair, marked_entries)


def resynthesize_marked(config: InferenceConfig):
    def resynthesize_(marked_srt_pair: MarkedSrtPair) -> MarkedSrtPair:
        for marked_idx, entry in enumerate(marked_srt_pair.marked_entries):
            logger.info(f"Resynthesizing: {entry.text}")

            text = preprocess_(entry.text)
            utterance = config.synthesizer.synthesize(text)

            marked_srt_pair.update(idx_in_full_srt=entry.idx - 1, idx_in_marked_srt=marked_idx, utterance=utterance)

        return marked_srt_pair

    return resynthesize_


def preprocess_(text: str) -> str:
    text = text.replace('*', '')
    text = re.sub('[ ]{2,}', '', text)
    text = text.strip()

    return text


if __name__ == '__main__':
    input_dir = Path("/home/arnas/Downloads/antanukas-in-progress-v1/out/replace-i-tilde-replace-ir-irgi")
    output_dir = input_dir / "out"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    speaker = Speaker.AURIMAS_ALTORIU_SESELY_22
    speed_multiplier = 0.85  # 1.0 - full speed; lower - faster
    device = 'gpu'
    cuda_device = 1

    config = get_inference_configs(speakers=[speaker], speed_multiplier=speed_multiplier,
                                   device=device, cuda_device=cuda_device)[speaker]

    srt_pairs = [
        SrtPair.from_filepaths_pair(srt_path=input_dir / file, audio_path=input_dir / file.replace('.srt', '.wav'))
        for file in os.listdir(input_dir) if file.endswith('.srt')]
    srt_pairs = map(log_filename, srt_pairs)
    marked_srt_pairs = map(filter_marked_entries, srt_pairs)
    marked_srt_pairs = map(resynthesize_marked(config), marked_srt_pairs)

    for marked_srt_pair in marked_srt_pairs:
        marked_srt_pair.save(output_dir)

    logger.info("SRT fixing complete!")
