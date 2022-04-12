from dataclasses import replace

from phonemizer import phonemize

from libs.dataset.core import SampleEntry
from logger import get_logger

logger = get_logger(__name__)


def phonemize_entry(entry: SampleEntry):
    phonemized_text = phonemize(entry.text, language='lt', backend='espeak', strip=True)
    return replace(entry, text=phonemized_text)
