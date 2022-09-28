""" from https://github.com/keithito/tacotron """
import re
import unicodedata

import torch

from src.model.commons import intersperse
from src.text import cleaners


def preprocess_text(text, cleaner_names, symbol_to_id, add_blank=True):
    text_norm = tokenize(text, cleaner_names, symbol_to_id)

    if add_blank:
        text_norm = intersperse(text_norm, 0)

    return torch.LongTensor(text_norm)


def tokenize(text, cleaner_names, symbol_to_id):
    """Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
      Args:
        text: string to convert to a sequence
        cleaner_names: names of the cleaner functions to run the text through
      Returns:
        List of integers corresponding to the symbols in the text
    """
    clean_text = __clean_text(text, cleaner_names)
    return [symbol_to_id[symbol] for symbol in clean_text]


def __clean_text(text, cleaner_names):
    for name in cleaner_names:
        cleaner = getattr(cleaners, name)
        if not cleaner:
            raise Exception('Unknown cleaner: %s' % name)

        text = cleaner(text)
    return text


def text_to_filename(text):
    text = text.lower()
    text = __normalize(text)
    text = re.sub(r'[^\w\s]', '', text).strip()  # remove non letter symbols
    return '_'.join(text.split(' ')[:8])


def __normalize(text):
    """
    Normalize text to ascii representation.
    E.g. input -> output: "kuo galėčiau jums padėti?" -> "kuo galeciau jums padeti"
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
