import re
from dataclasses import dataclass
from io import BytesIO

import unicodedata
from numpy import ndarray
from scipy.io.wavfile import write
from pydub import AudioSegment


@dataclass
class SynthesizedUtterance:
    text: str
    audio: ndarray
    sample_rate: int
    filename: str = None

    @classmethod
    def from_text_and_audio(cls, text: str, audio: ndarray, sample_rate: int):
        return cls(text=text, audio=audio, sample_rate=sample_rate, filename=cls.__text_to_filename(text))

    @classmethod
    def __text_to_filename(self, text):
        text = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[^\w\s]', '', text).strip()  # remove non letter symbols
        return '_'.join(text.split(' ')[:8])

    @property
    def duration(self):
        # duration in milliseconds
        return len(self.audio) / self.sample_rate * 1000

    @property
    def audio_segment(self):
        tmp_bytes = BytesIO()
        write(tmp_bytes, rate=self.sample_rate, data=self.audio)
        return AudioSegment.from_wav(tmp_bytes)


