import re
from text.japanese import japanese_to_romaji_with_accent, japanese_to_ipa, japanese_to_ipa2, japanese_to_ipa3
from text.korean import latin_to_hangul, number_to_hangul, divide_hangul, korean_to_lazy_ipa, korean_to_ipa
from text.mandarin import number_to_chinese, chinese_to_bopomofo, latin_to_bopomofo, chinese_to_romaji, chinese_to_lazy_ipa, chinese_to_ipa, chinese_to_ipa2
from text.sanskrit import devanagari_to_ipa
from text.english import english_to_lazy_ipa, english_to_ipa2, english_to_lazy_ipa2
from text.thai import num_to_thai, latin_to_thai
from text.shanghainese import shanghainese_to_ipa
from text.cantonese import cantonese_to_ipa
from text.ngu_dialect import ngu_dialect_to_ipa


def japanese_cleaners(text):
    text = japanese_to_romaji_with_accent(text)
    text = re.sub(r'([A-Za-z])$', r'\1.', text)
    return text


def japanese_cleaners2(text):
    return japanese_cleaners(text).replace('ts', 'ʦ').replace('...', '…')


def korean_cleaners(text):
    '''Pipeline for Korean text'''
    text = latin_to_hangul(text)
    text = number_to_hangul(text)
    text = divide_hangul(text)
    text = re.sub(r'([\u3131-\u3163])$', r'\1.', text)
    return text


def chinese_cleaners(text):
    '''Pipeline for Chinese text'''
    text = number_to_chinese(text)
    text = chinese_to_bopomofo(text)
    text = latin_to_bopomofo(text)
    text = re.sub(r'([ˉˊˇˋ˙])$', r'\1。', text)
    return text


def zh_ja_mixture_cleaners(text):
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_romaji(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]', lambda x: japanese_to_romaji_with_accent(
        x.group(1)).replace('ts', 'ʦ').replace('u', 'ɯ').replace('...', '…')+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def sanskrit_cleaners(text):
    text = text.replace('॥', '।').replace('ॐ', 'ओम्')
    text = re.sub(r'([^।])$', r'\1।', text)
    return text


def cjks_cleaners(text):
    chinese_texts = re.findall(r'\[ZH\].*?\[ZH\]', text)
    japanese_texts = re.findall(r'\[JA\].*?\[JA\]', text)
    korean_texts = re.findall(r'\[KO\].*?\[KO\]', text)
    sanskrit_texts = re.findall(r'\[SA\].*?\[SA\]', text)
    english_texts = re.findall(r'\[EN\].*?\[EN\]', text)
    for chinese_text in chinese_texts:
        cleaned_text = chinese_to_lazy_ipa(chinese_text[4:-4])
        text = text.replace(chinese_text, cleaned_text+' ', 1)
    for japanese_text in japanese_texts:
        cleaned_text = japanese_to_ipa(japanese_text[4:-4])
        text = text.replace(japanese_text, cleaned_text+' ', 1)
    for korean_text in korean_texts:
        cleaned_text = korean_to_lazy_ipa(korean_text[4:-4])
        text = text.replace(korean_text, cleaned_text+' ', 1)
    for sanskrit_text in sanskrit_texts:
        cleaned_text = devanagari_to_ipa(sanskrit_text[4:-4])
        text = text.replace(sanskrit_text, cleaned_text+' ', 1)
    for english_text in english_texts:
        cleaned_text = english_to_lazy_ipa(english_text[4:-4])
        text = text.replace(english_text, cleaned_text+' ', 1)
    text = text[:-1]
    if re.match(r'[^\.,!\?\-…~]', text[-1]):
        text += '.'
    return text


def cjke_cleaners(text):
    chinese_texts = re.findall(r'\[ZH\].*?\[ZH\]', text)
    japanese_texts = re.findall(r'\[JA\].*?\[JA\]', text)
    korean_texts = re.findall(r'\[KO\].*?\[KO\]', text)
    english_texts = re.findall(r'\[EN\].*?\[EN\]', text)
    for chinese_text in chinese_texts:
        cleaned_text = chinese_to_lazy_ipa(chinese_text[4:-4])
        cleaned_text = cleaned_text.replace(
            'ʧ', 'tʃ').replace('ʦ', 'ts').replace('ɥan', 'ɥæn')
        text = text.replace(chinese_text, cleaned_text+' ', 1)
    for japanese_text in japanese_texts:
        cleaned_text = japanese_to_ipa(japanese_text[4:-4])
        cleaned_text = cleaned_text.replace('ʧ', 'tʃ').replace(
            'ʦ', 'ts').replace('ɥan', 'ɥæn').replace('ʥ', 'dz')
        text = text.replace(japanese_text, cleaned_text+' ', 1)
    for korean_text in korean_texts:
        cleaned_text = korean_to_ipa(korean_text[4:-4])
        text = text.replace(korean_text, cleaned_text+' ', 1)
    for english_text in english_texts:
        cleaned_text = english_to_ipa2(english_text[4:-4])
        cleaned_text = cleaned_text.replace('ɑ', 'a').replace(
            'ɔ', 'o').replace('ɛ', 'e').replace('ɪ', 'i').replace('ʊ', 'u')
        text = text.replace(english_text, cleaned_text+' ', 1)
    text = text[:-1]
    if re.match(r'[^\.,!\?\-…~]', text[-1]):
        text += '.'
    return text


def cjke_cleaners2(text):
    chinese_texts = re.findall(r'\[ZH\].*?\[ZH\]', text)
    japanese_texts = re.findall(r'\[JA\].*?\[JA\]', text)
    korean_texts = re.findall(r'\[KO\].*?\[KO\]', text)
    english_texts = re.findall(r'\[EN\].*?\[EN\]', text)
    for chinese_text in chinese_texts:
        cleaned_text = chinese_to_ipa(chinese_text[4:-4])
        text = text.replace(chinese_text, cleaned_text+' ', 1)
    for japanese_text in japanese_texts:
        cleaned_text = japanese_to_ipa2(japanese_text[4:-4])
        text = text.replace(japanese_text, cleaned_text+' ', 1)
    for korean_text in korean_texts:
        cleaned_text = korean_to_ipa(korean_text[4:-4])
        text = text.replace(korean_text, cleaned_text+' ', 1)
    for english_text in english_texts:
        cleaned_text = english_to_ipa2(english_text[4:-4])
        text = text.replace(english_text, cleaned_text+' ', 1)
    text = text[:-1]
    if re.match(r'[^\.,!\?\-…~]', text[-1]):
        text += '.'
    return text


def thai_cleaners(text):
    text = num_to_thai(text)
    text = latin_to_thai(text)
    return text


def shanghainese_cleaners(text):
    text = shanghainese_to_ipa(text)
    if re.match(r'[^\.,!\?\-…~]', text[-1]):
        text += '.'
    return text


def chinese_dialect_cleaners(text):
    text = re.sub(r'\[MD\](.*?)\[MD\]',
                  lambda x: chinese_to_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\[TW\](.*?)\[TW\]',
                  lambda x: chinese_to_ipa2(x.group(1), True)+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]',
                  lambda x: japanese_to_ipa3(x.group(1)).replace('Q', 'ʔ')+' ', text)
    text = re.sub(r'\[SH\](.*?)\[SH\]', lambda x: shanghainese_to_ipa(x.group(1)).replace('1', '˥˧').replace('5',
                  '˧˧˦').replace('6', '˩˩˧').replace('7', '˥').replace('8', '˩˨').replace('ᴀ', 'ɐ').replace('ᴇ', 'e')+' ', text)
    text = re.sub(r'\[GD\](.*?)\[GD\]',
                  lambda x: cantonese_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]',
                  lambda x: english_to_lazy_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\[([A-Z]{2})\](.*?)\[\1\]', lambda x: ngu_dialect_to_ipa(x.group(2), x.group(
        1)).replace('ʣ', 'dz').replace('ʥ', 'dʑ').replace('ʦ', 'ts').replace('ʨ', 'tɕ')+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text
