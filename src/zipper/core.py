import re
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from scipy.io.wavfile import read, write
from unidecode import unidecode

from src.file import read_txt

csv_delimiter = '|'

oov_replacement_vocabulary = {
    '_': ' ',
    '«': '',
    '\xad': '',
    '®': '',
    '°': '',
    '²': '',
    '»': '',
    'ʼ': "'",
    '˚': '',
    '‒': '-',
    '–': '-',
    '—': '-',
    '─': '-',
    '‘': "'",
    '’': "'",
    '“': '"',
    '”': '"',
    '„': '"',
    '•': '',
    '\\\\': '',
    ',,': '"',
}

letter_replacements = {
    "a": "aã",
    "b": "bė̃",
    "c": "cė̃",
    "č": "čė̃",
    "d": "dė̃",
    "e": "eẽ",
    "ę": "ęę̃",
    "ė": "ėė̃",
    "f": "ef̃",
    "g": "gė̃",
    "h": "hãš",
    "i": "iĩ",
    # "į": "įį̃",
    "y": "ỹgrek",
    "j": "jo\u0300t",
    "k": "kã",
    "l": "el̃",
    "m": "em̃",
    "n": "eñ",
    # "o": "oõ",
    "p": "pė̃",
    "r": "er̃",
    "s": "es̃",
    "š": "eš̃",
    "t": "tė̃",
    "u": "uũ",
    "ų": "ųų̃",
    "ū": "ūū̃",
    "v": "vė̃",
    "z": "ze\u0300t",
    "ž": "žė̃",
}


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


@dataclass
class InOutPair:
    in_filepath: Path
    out_directory: Path


@dataclass
class FilelistEntry:
    path: Path
    text: str

    def remove_text_accents(self):
        return re.sub(r'[\u0300\u0301\u0303]', '', self.text)


@dataclass
class TestSet:
    in_out_pair: InOutPair
    entries: List[FilelistEntry]

    def copy_wavs(self):
        self.in_out_pair.out_directory.mkdir(parents=True, exist_ok=True)
        for entry in self.entries:
            sr, wav = read(entry.path)
            write(self.in_out_pair.out_directory / entry.path.name, sr, wav)

    def save_out_filelist(self, include_non_stressed=False):
        if include_non_stressed:
            entry_lines = [f"{entry.path.name}|{entry.text}|{entry.remove_text_accents()}" for entry in self.entries]
        else:
            entry_lines = [f"{entry.path.name}|{entry.text}" for entry in self.entries]

        text = '\n'.join(entry_lines)
        with open(self.in_out_pair.out_directory / self.in_out_pair.in_filepath.name, mode='w', encoding='utf-8') as f:
            f.write(text)

    @classmethod
    def from_in_out_pair(cls, in_out_pair: InOutPair):
        text = read_txt(in_out_pair.in_filepath)
        lines = text.split('\n')
        split_lines = [line.split('|') for line in lines]

        return cls(
            in_out_pair=in_out_pair,
            entries=[FilelistEntry(path=Path(line[0]), text=line[1]) for line in split_lines]
        )
