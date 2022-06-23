from dataclasses import dataclass, replace
from io import BytesIO
from pathlib import Path
from typing import List

from numpy import ndarray
from numpy.typing import ArrayLike
from pydub import AudioSegment
from scipy.io.wavfile import write

from src.logger import get_logger
from src.text.cleaners import collapse_whitespace
from src.text.convert import text_to_filename
from src.time import format_milliseconds_as_srt_time, srt_time_to_millisecond_float

logger = get_logger(__name__)


@dataclass
class Sample:
    audio: ArrayLike
    text: str
    sample_rate: int = None


@dataclass
class SynthesizedUtterance:
    text: str
    audio: ndarray
    sample_rate: int
    filename: str = None

    @classmethod
    def from_text_and_audio(cls, text: str, audio: ndarray, sample_rate: int):
        return cls(text=text, audio=audio, sample_rate=sample_rate, filename=text_to_filename(text))

    @property
    def duration(self):
        # duration in milliseconds
        return len(self.audio) / self.sample_rate * 1000

    @property
    def audio_segment(self):
        tmp_bytes = BytesIO()
        write(tmp_bytes, rate=self.sample_rate, data=self.audio)
        return AudioSegment.from_wav(tmp_bytes)


@dataclass
class SrtEntry:
    idx: int
    start: float
    end: float
    text: str
    audio: AudioSegment

    @classmethod
    def from_entry(cls, entry: str, audio: AudioSegment = None):
        """
        `entry` is of format:
        <idx>
        <start-time> --> <end-time>
        <text>
        """
        entry = entry.strip()
        entry_lines = entry.split('\n')
        idx = int(entry_lines[0])
        start, end = cls.__extract_times_from_srt_entry(entry_lines)
        text = cls.__extract_text_from_srt_entry(entry_lines)

        audio_segment = audio[start:end] if audio else None

        return cls(idx=idx, start=start, end=end, text=text, audio=audio_segment)

    @classmethod
    def __extract_times_from_srt_entry(cls, entry: List[str]):
        times = entry[1]
        start, end = times.split(' --> ')
        return srt_time_to_millisecond_float(start), srt_time_to_millisecond_float(end)

    @classmethod
    def __extract_text_from_srt_entry(cls, entry: List[str]):
        text = ' '.join(entry[2:])
        text = collapse_whitespace(text)
        return text.strip()

    def to_string(self):
        start = format_milliseconds_as_srt_time(self.start)
        end = format_milliseconds_as_srt_time(self.end)
        return f"{self.idx}\n{start} --> {end}\n{self.text}"


@dataclass
class SrtPair:
    entries: List[SrtEntry]
    audio: AudioSegment
    filename: str

    @classmethod
    def from_filepaths_pair(cls, srt_path: Path, audio_path: Path):
        audio = AudioSegment.from_wav(audio_path)
        entries = cls.__srt_file_to_entries(srt_path, audio)
        filename = srt_path.stem

        return cls(entries=entries, audio=audio, filename=filename)

    @classmethod
    def __srt_file_to_entries(cls, filepath, audio: AudioSegment = None) -> List[SrtEntry]:
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            srt_file_contents = f.read().strip()

        return [SrtEntry.from_entry(entry_str, audio) for entry_str in srt_file_contents.split('\n\n')]

    def update_entry_by_utternace(self, idx: int, utterance: SynthesizedUtterance):
        self.__insert_segment_to_audio(utterance.audio_segment, self.entries[idx])
        self.__update_srt_by_utterance(idx, utterance)

    def __insert_segment_to_audio(self, segment: AudioSegment, entry: SrtEntry):
        self.audio = self.audio[0:entry.start] + segment + self.audio[entry.end:]

    def __update_srt_by_utterance(self, idx: int, utterance: SynthesizedUtterance):
        old_entry = self.entries[idx]
        offset = utterance.duration - (old_entry.end - old_entry.start)
        self.entries[idx] = replace(old_entry,
                                    end=old_entry.end + offset,
                                    text=utterance.text,
                                    audio=utterance.audio_segment)

        for i, entry in enumerate(self.entries[idx + 1:], start=idx+1):
            self.entries[i] = replace(entry, start=entry.start + offset, end=entry.end + offset)

    def save_pair(self, output_dir: Path):
        self.__save_srt(output_dir)
        self.__save_audio(output_dir)

    def __save_srt(self, output_dir: Path):
        logger.info(f"Saving SRT file to {output_dir}")
        text = '\n\n'.join([srt_entry.to_string() for srt_entry in self.entries])
        with open(output_dir / f"{self.filename}.srt", mode='w', encoding='utf-8') as f:
            f.write(text)

    def __save_audio(self, output_dir: Path):
        logger.info(f"Saving WAV file to {output_dir}")
        self.audio.export(output_dir / f"{self.filename}.wav", format='wav')
