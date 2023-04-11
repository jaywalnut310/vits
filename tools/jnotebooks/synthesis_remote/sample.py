from dataclasses import dataclass
from numpy import ndarray


@dataclass
class Sample:
    audio: ndarray
    text: str