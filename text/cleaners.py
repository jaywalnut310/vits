""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from phonemizer import phonemize
from pypinyin import pinyin, lazy_pinyin, load_phrases_dict, Style, load_single_dict
from pypinyin.style._utils import get_finals, get_initials
from pypinyin_dict.phrase_pinyin_data import cc_cedict
from pypinyin_dict.pinyin_data import kmandarin_8105
import jieba
kmandarin_8105.load()
cc_cedict.load()
PHRASE_LIST = [
  "琴", "安柏", "丽莎", "凯亚", "芭芭拉", "迪卢克", "雷泽", "温迪", "可莉", "班尼特", "诺艾尔", "菲谢尔",
  "砂糖", "莫娜", "迪奥娜", "阿贝多", "罗莎莉亚", "优菈", "魈", "北斗", "凝光", "香菱", "行秋", "重云",
  "七七", "刻晴", "达达利亚", "钟离", "辛焱", "甘雨", "胡桃", "烟绯", "申鹤", "云堇", "夜兰", "神里绫华",
  "神里", "绫华", "枫原万叶", "枫原", "万叶", "宵宫", "早柚", "雷电将军", "九条裟罗", "九条", "裟罗", "珊瑚宫心海",
  "珊瑚宫", "心海", "托马", "荒泷", "一斗", "荒泷派", "五郎", "八重神子", "神子", "神里绫人", "绫人",
  "久岐忍", "鹿野院平藏", "平藏", "蒙德", "璃月", "稻妻", "北风的王狼", "风魔龙", "特瓦林", "若陀龙王", "龙脊雪山",
  "金苹果群岛", "渊下宫", "层岩巨渊", "奥赛尔", "七天神像", "钩钩果", "落落莓", "塞西莉亚花", "风车菊", "尘歌壶",
  "提瓦特", "明冠山地", "风龙废墟", "明冠峡", "坠星山谷", "果酒湖", "望风山地", "坎瑞亚", "须弥", "枫丹", "纳塔",
  "至冬", "丘丘人", "丘丘暴徒", "深渊法师", "深渊咏者", "盗宝团", "愚人众", "深渊教团", "骗骗花", "急冻树", "龙蜥",
  "鸣神岛", "神无冢", "八酝岛", "海祇岛", "清籁岛", "鹤观", "绝云间", "群玉阁", "南十字", "死兆星", "木漏茶室", "神樱",
  "鸣神大社", "天使的馈赠", "社奉行", "勘定奉行", "天领奉行", "夜叉", "风神", "岩神", "雷神", "风之神", "岩之神", "雷之神",
  "风神瞳", "岩神瞳", "雷神瞳", "摩拉克斯", "契约之神", "雷电影", "雷电真", "八重宫司", "宫司大人", "巴巴托斯", "玉衡星",
  "天权星", "璃月七星", "留云借风", "削月筑阳", "理水叠山", "请仙典仪"
]

for phrase in PHRASE_LIST:
    jieba.add_word(phrase)

load_phrases_dict({"若陀": [["rě"], ["tuó"]], "平藏": [["píng"], ["zàng"]],
    "派蒙": [["pài"], ["méng"]], "安柏": [["ān"], ["bó"]],
    "一斗": [["yī"], ["dǒu"]]
    })

# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
  ('mrs', 'misess'),
  ('mr', 'mister'),
  ('dr', 'doctor'),
  ('st', 'saint'),
  ('co', 'company'),
  ('jr', 'junior'),
  ('maj', 'major'),
  ('gen', 'general'),
  ('drs', 'doctors'),
  ('rev', 'reverend'),
  ('lt', 'lieutenant'),
  ('hon', 'honorable'),
  ('sgt', 'sergeant'),
  ('capt', 'captain'),
  ('esq', 'esquire'),
  ('ltd', 'limited'),
  ('col', 'colonel'),
  ('ft', 'fort'),
]]


def expand_abbreviations(text):
  for regex, replacement in _abbreviations:
    text = re.sub(regex, replacement, text)
  return text


def expand_numbers(text):
  return normalize_numbers(text)


def lowercase(text):
  return text.lower()


def collapse_whitespace(text):
  return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
  return unidecode(text)

def chinese_cleaners(text):
  return " ".join(lazy_pinyin(jieba.cut(text), style=Style.TONE3, errors='ignore'))

def chinese_cleaners2(text):
  return " ".join([
    p
    for phone in pinyin(text, style=Style.TONE3, v_to_u=True)
    for p in [
      get_initials(phone[0], strict=True),
      get_finals(phone[0][:-1], strict=True) + phone[0][-1]
      if phone[0][-1].isdigit()
      else get_finals(phone[0], strict=True)
      if phone[0][-1].isalnum()
      else phone[0],
    ]
    if len(p) != 0 and not p.isdigit()
  ])

def basic_cleaners(text):
  '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def transliteration_cleaners(text):
  '''Pipeline for non-English text that transliterates to ASCII.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def english_cleaners(text):
  '''Pipeline for English text, including abbreviation expansion.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_abbreviations(text)
  phonemes = phonemize(text, language='en-us', backend='espeak', strip=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes


def english_cleaners2(text):
  '''Pipeline for English text, including abbreviation expansion. + punctuation + stress'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_abbreviations(text)
  phonemes = phonemize(text, language='en-us', backend='espeak', strip=True, preserve_punctuation=True, with_stress=True)
  phonemes = collapse_whitespace(phonemes)
  return phonemes
