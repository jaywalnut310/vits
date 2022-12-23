import multiprocessing
from typing import List, Union

from phonemizer import phonemize

from src.logger import get_logger

logger = get_logger(__name__)


def phonemize_(text: Union[str, List[str]], language='lt'):
    # English language: en-us
    # Lithuanian language: lt

    njobs = multiprocessing.cpu_count()
    return phonemize(
        text,
        language=language,
        backend='espeak',
        strip=True,
        preserve_punctuation=True,
        with_stress=True,
        njobs=njobs
    )
