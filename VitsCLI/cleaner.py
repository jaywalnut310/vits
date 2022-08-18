import re

import pyopenjtalk
from unidecode import unidecode

_japanese_characters = re.compile(r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')
_japanese_marks = re.compile(r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')


def japanese_cleaner(text):
  sentences = re.split(_japanese_marks, text)
  marks = re.findall(_japanese_marks, text)
  text = ''
  for i, sentence in enumerate(sentences):
    if re.match(_japanese_characters, sentence):
      labels = pyopenjtalk.extract_fullcontext(sentence)
      for n, label in enumerate(labels):
        phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
        if phoneme not in ['sil', 'pau']:
          text += phoneme.replace('ch', 'ʧ').replace('sh', 'ʃ').replace('cl', 'Q').replace('ts', 'ʦ')
        else:
          continue
        a3 = int(re.search(r"\+(\d+)/", label).group(1))
        if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil', 'pau']:
          a2_next = -1
        else:
          a2_next = int(re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
        # Accent phrase boundary
        if a3 == 1 and a2_next == 1:
          text += ' '
    if i < len(marks):
      text += unidecode(marks[i]).replace(' ', '')
  if re.match('[A-Za-z]', text[-1]):
    text += '.'
  return text.replace('...', '…')
