import re
import string

from libs.dataset.core import SampleEntry, oov_replacement_vocabulary, letter_replacements

__word_start_regex = f'[ \t\n]|^|[{string.punctuation}]'
__word_end_regex = f'[ \t\n]|$|[{string.punctuation}]'

def does_not_have_numbers(s: SampleEntry):
    return not any(char.isdigit() for char in s.text)


def waveform_not_longer_than(target_length):
    def step(s: SampleEntry):
        return s.duration < target_length

    return step


def waveform_not_shorter_than(target_length):
    def step(s: SampleEntry):
        return s.duration > target_length

    return step


def replace_oov(line):
    for symbol, replacement in oov_replacement_vocabulary.items():
        line = re.sub(fr"{symbol}", replacement, line)
    line = re.sub(r"[ ]{2,}", ' ', line)
    line = re.sub(r"\n\s*\n", r'\n', line)
    return line


def test_replace_oov():
    assert replace_oov("vien_as") == "vien as"
    assert replace_oov("vien«as") == "vienas"
    assert replace_oov("vien\xadas") == "vienas"
    assert replace_oov("vien®as") == "vienas"
    assert replace_oov("vien°as") == "vienas"
    assert replace_oov("vien²as") == "vienas"
    assert replace_oov("vien»as") == "vienas"
    assert replace_oov("vienʼas") == "vien'as"
    assert replace_oov("vien˚as") == "vienas"
    assert replace_oov("vien‒as") == "vien-as"
    assert replace_oov("vien–as") == "vien-as"
    assert replace_oov("vien—as") == "vien-as"
    assert replace_oov("vien‘as") == "vien'as"
    assert replace_oov("vien’as") == "vien'as"
    assert replace_oov("vien“as") == 'vien"as'
    assert replace_oov("vien”as") == 'vien"as'
    assert replace_oov("vien„as") == 'vien"as'
    assert replace_oov("vien\\as") == "vienas"
    assert replace_oov("vien,,as") == 'vien"as'


def replace_letter_to_sound(line):
    for letter, sound in letter_replacements.items():
        line = re.sub(fr"({__word_start_regex})[{letter.lower()}{letter.upper()}]+({__word_end_regex})", fr"\1{sound}\2", line)
    return line

def test_replace_letter_to_sound():
    assert replace_letter_to_sound("aAa b C d e f g h I J k L M n") == "aã bė̃ cė̃ dė̃ eẽ ef̃ gė̃ hãš iĩ jòt kã el̃ em̃ eñ"
    assert replace_letter_to_sound("vienas du aaaa") == "vienas du aã"
