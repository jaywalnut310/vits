from dataclasses import dataclass
import numpy as np


@dataclass
class Paragraph:
    index: int  # index in chapter
    text: str


@dataclass
class Sentence:
    index: int  # index in paragraph
    paragraph_idx: int # paragraph index in chapter
    text: str
    audio: np.array = None
