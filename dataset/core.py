import re
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from unidecode import unidecode

csv_delimiter = '|'


@dataclass
class AudioRecordMetadata:
    text: str
    zip_entry_name: str
    sample_rate: int
    sample_count: int
    id: str
    group: str
    batch: int
    seq_no: int
    bitrate: str = None
    format: Optional[str] = None

    @property
    def duration(self):
        return float(self.sample_count) / self.sample_rate


@dataclass
class SampleEntry:
    audio_bytes: bytes
    sample_rate: int
    text: str
    filepath: str
    duration: float

    def as_list(self):
        return [self.filepath, self.text]

    def as_csv_string(self):
        return csv_delimiter.join(self.as_list())

    @classmethod
    def from_zip_sample_entry(cls, audio_bytes: bytes, metadata: AudioRecordMetadata, output_dataset_dir: str,
                              zipfile_idx: int, audio_idx: int):
        normalized_text = SampleEntry.__normalize_text(metadata.text)
        filepath = Path(output_dataset_dir) / f"MIF{zipfile_idx:04d}_{audio_idx:04d}_{normalized_text}.wav"
        duration = metadata.sample_count / metadata.sample_rate
        return cls(audio_bytes=audio_bytes,
                   sample_rate=metadata.sample_rate,
                   text=metadata.text,
                   filepath=str(filepath),
                   duration=duration)

    @classmethod
    def __normalize_text(cls, text):
        text = unidecode(text)
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r"\n", '', text)
        return '_'.join(text.split()[:8]).strip()


@dataclass
class DatasetEntry:
    filepath: str
    text: str

    def as_list(self):
        return [self.filepath, self.text]

    def as_string(self):
        return csv_delimiter.join(self.as_list())


def to_dataset_entry(sample_entry: SampleEntry):
    return DatasetEntry(filepath=sample_entry.filepath, text=sample_entry.text)
