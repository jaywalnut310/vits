import re
import opencc


dialects = {'SZ': 'suzhou', 'WX': 'wuxi', 'CZ': 'changzhou', 'HZ': 'hangzhou',
            'SX': 'shaoxing', 'NB': 'ningbo', 'JJ': 'jingjiang', 'YX': 'yixing',
            'JD': 'jiading', 'ZR': 'zhenru', 'PH': 'pinghu', 'TX': 'tongxiang',
            'JS': 'jiashan', 'XS': 'xiashi', 'LP': 'linping', 'XS': 'xiaoshan',
            'FY': 'fuyang', 'RA': 'ruao', 'CX': 'cixi', 'SM': 'sanmen', 'TT': 'tiantai'}

converters = {}

for dialect in dialects.values():
    try:
        converters[dialect] = opencc.OpenCC(dialect)
    except:
        pass


def ngu_dialect_to_ipa(text, dialect):
    dialect = dialects[dialect]
    text = converters[dialect].convert(text).replace('$',' ')
    text = re.sub(r'[、；：]', '，', text)
    text = re.sub(r'\s*，\s*', ', ', text)
    text = re.sub(r'\s*。\s*', '. ', text)
    text = re.sub(r'\s*？\s*', '? ', text)
    text = re.sub(r'\s*！\s*', '! ', text)
    text = re.sub(r'\s*$', '', text)
    return text
