from dataclasses import replace

from phonemizer import phonemize

from src.logger import get_logger
from src.zipper.core import SampleEntry

logger = get_logger(__name__)


def phonemize_entry(entry: SampleEntry):
    phonemized_text = phonemize(entry.text, language='lt', backend='espeak', strip=True)
    return replace(entry, text=phonemized_text)
