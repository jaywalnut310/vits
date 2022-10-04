import re
from text.japanese import japanese_to_romaji_with_accent, japanese_to_ipa, japanese_to_ipa2
from text.korean import latin_to_hangul, number_to_hangul, divide_hangul, korean_to_lazy_ipa, korean_to_ipa
from text.mandarin import number_to_chinese, chinese_to_bopomofo, latin_to_bopomofo, chinese_to_romaji, chinese_to_lazy_ipa, chinese_to_ipa
from text.sanskrit import devanagari_to_ipa
from text.english import english_to_lazy_ipa, english_to_ipa2
from text.thai import num_to_thai, latin_to_thai
from text.shanghainese import shanghainese_to_ipa


def japanese_cleaners(text):
    text = japanese_to_romaji_with_accent(text)
    if re.match('[A-Za-z]', text[-1]):
        text += '.'
    return text


def japanese_cleaners2(text):
    return japanese_cleaners(text).replace('ts', 'ʦ').replace('...', '…')


def korean_cleaners(text):
    '''Pipeline for Korean text'''
    text = latin_to_hangul(text)
    text = number_to_hangul(text)
    text = divide_hangul(text)
    if re.match('[\u3131-\u3163]', text[-1]):
        text += '.'
    return text


def chinese_cleaners(text):
    '''Pipeline for Chinese text'''
    text = number_to_chinese(text)
    text = chinese_to_bopomofo(text)
    text = latin_to_bopomofo(text)
    if re.match('[ˉˊˇˋ˙]', text[-1]):
        text += '。'
    return text


def zh_ja_mixture_cleaners(text):
    chinese_texts = re.findall(r'\[ZH\].*?\[ZH\]', text)
    japanese_texts = re.findall(r'\[JA\].*?\[JA\]', text)
    for chinese_text in chinese_texts:
        cleaned_text = chinese_to_romaji(chinese_text[4:-4])
        text = text.replace(chinese_text, cleaned_text+' ', 1)
    for japanese_text in japanese_texts:
        cleaned_text = japanese_to_romaji_with_accent(
            japanese_text[4:-4]).replace('ts', 'ʦ').replace('u', 'ɯ').replace('...', '…')
        text = text.replace(japanese_text, cleaned_text+' ', 1)
    text = text[:-1]
    if re.match('[A-Za-zɯɹəɥ→↓↑]', text[-1]):
        text += '.'
    return text


def sanskrit_cleaners(text):
    text = text.replace('॥', '।').replace('ॐ', 'ओम्')
    if text[-1] != '।':
        text += ' ।'
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
