from dataclasses import dataclass

from numpy import ndarray
from numpy.typing import ArrayLike

from src.text.convert import text_to_filename
from src.time import format_milliseconds_as_srt_time


@dataclass
class Sample:
    audio: ArrayLike
    text: str
    sample_rate: int = None


@dataclass
class SrtEntry:
    idx: int
    start: float
    end: float
    text: str

    def to_string(self):
        start = format_milliseconds_as_srt_time(self.start)
        end = format_milliseconds_as_srt_time(self.end)
        return f"{self.idx}\n{start} --> {end}\n{self.text}"


@dataclass
class SynthesizedUtterance:
    text: str
    audio: ndarray
    sample_rate: int
    filename: str = None

    @classmethod
    def from_text_and_audio(cls, text: str, audio: ndarray, sample_rate: int):
        return cls(text=text, audio=audio, sample_rate=sample_rate, filename=text_to_filename(text))
