import re
from unidecode import unidecode
import pyopenjtalk


# Regular expression matching Japanese without punctuation marks:
_japanese_characters = re.compile(
    r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Regular expression matching non-Japanese characters or punctuation marks:
_japanese_marks = re.compile(
    r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# List of (symbol, Japanese) pairs for marks:
_symbols_to_japanese = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('％', 'パーセント')
]]

# List of (romaji, ipa) pairs for marks:
_romaji_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ts', 'ʦ'),
    ('u', 'ɯ'),
    ('j', 'ʥ'),
    ('y', 'j'),
    ('ni', 'n^i'),
    ('nj', 'n^'),
    ('hi', 'çi'),
    ('hj', 'ç'),
    ('f', 'ɸ'),
    ('I', 'i*'),
    ('U', 'ɯ*'),
    ('r', 'ɾ')
]]

# List of (romaji, ipa2) pairs for marks:
_romaji_to_ipa2 = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('u', 'ɯ'),
    ('ʧ', 'tʃ'),
    ('j', 'dʑ'),
    ('y', 'j'),
    ('ni', 'n^i'),
    ('nj', 'n^'),
    ('hi', 'çi'),
    ('hj', 'ç'),
    ('f', 'ɸ'),
    ('I', 'i*'),
    ('U', 'ɯ*'),
    ('r', 'ɾ')
]]

# Dictinary of (consonant, sokuon) pairs:
_real_sokuon = {
  'k': 'k#',
  'g': 'k#',
  't': 't#',
  'd': 't#',
  'ʦ': 't#',
  'ʧ': 't#',
  'ʥ': 't#',
  'j': 't#',
  's': 's',
  'ʃ': 's',
  'p': 'p#',
  'b': 'p#'
}

# Dictinary of (consonant, hatsuon) pairs:
_real_hatsuon = {
  'p': 'm',
  'b': 'm',
  'm': 'm',
  't': 'n',
  'd': 'n',
  'n': 'n',
  'ʧ': 'n^',
  'ʥ': 'n^',
  'k': 'ŋ',
  'g': 'ŋ'
}


def symbols_to_japanese(text):
    for regex, replacement in _symbols_to_japanese:
        text = re.sub(regex, replacement, text)
    return text


def japanese_to_romaji_with_accent(text):
    '''Reference https://r9y9.github.io/ttslearn/latest/notebooks/ch10_Recipe-Tacotron.html'''
    text = symbols_to_japanese(text)
    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)
    text = ''
    for i, sentence in enumerate(sentences):
        if re.match(_japanese_characters, sentence):
            if text != '':
                text += ' '
            labels = pyopenjtalk.extract_fullcontext(sentence)
            for n, label in enumerate(labels):
                phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
                if phoneme not in ['sil', 'pau']:
                    text += phoneme.replace('ch', 'ʧ').replace('sh',
                                                               'ʃ').replace('cl', 'Q')
                else:
                    continue
                # n_moras = int(re.search(r'/F:(\d+)_', label).group(1))
                a1 = int(re.search(r"/A:(\-?[0-9]+)\+", label).group(1))
                a2 = int(re.search(r"\+(\d+)\+", label).group(1))
                a3 = int(re.search(r"\+(\d+)/", label).group(1))
                if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil', 'pau']:
                    a2_next = -1
                else:
                    a2_next = int(
                        re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
                # Accent phrase boundary
                if a3 == 1 and a2_next == 1:
                    text += ' '
                # Falling
                elif a1 == 0 and a2_next == a2 + 1:
                    text += '↓'
                # Rising
                elif a2 == 1 and a2_next == 2:
                    text += '↑'
        if i < len(marks):
            text += unidecode(marks[i]).replace(' ', '')
    return text


def get_real_sokuon(text):
  text=re.sub('Q[↑↓]*(.)',lambda x:_real_sokuon[x.group(1)]+x.group(0)[1:] if x.group(1) in _real_sokuon.keys() else x.group(0),text)
  return text


def get_real_hatsuon(text):
  text=re.sub('N[↑↓]*(.)',lambda x:_real_hatsuon[x.group(1)]+x.group(0)[1:] if x.group(1) in _real_hatsuon.keys() else x.group(0),text)
  return text


def japanese_to_ipa(text):
    text=japanese_to_romaji_with_accent(text).replace('...', '…')
    for regex, replacement in _romaji_to_ipa:
        text = re.sub(regex, replacement, text)
    text = re.sub(
            r'([A-Za-zɯ])\1+', lambda x: x.group(0)[0]+'ː'*(len(x.group(0))-1), text)
    text = get_real_sokuon(text)
    text = get_real_hatsuon(text)
    return text


def japanese_to_ipa2(text):
    text=japanese_to_romaji_with_accent(text).replace('...', '…')
    for regex, replacement in _romaji_to_ipa2:
        text = re.sub(regex, replacement, text)
    text = get_real_sokuon(text)
    text = get_real_hatsuon(text)
    return text
