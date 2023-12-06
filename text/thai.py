import re
from num_thai.thainumbers import NumThai


num = NumThai()

# List of (Latin alphabet, Thai) pairs:
_latin_to_thai = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('a', 'เอ'),
    ('b','บี'),
    ('c','ซี'),
    ('d','ดี'),
    ('e','อี'),
    ('f','เอฟ'),
    ('g','จี'),
    ('h','เอช'),
    ('i','ไอ'),
    ('j','เจ'),
    ('k','เค'),
    ('l','แอล'),
    ('m','เอ็ม'),
    ('n','เอ็น'),
    ('o','โอ'),
    ('p','พี'),
    ('q','คิว'),
    ('r','แอร์'),
    ('s','เอส'),
    ('t','ที'),
    ('u','ยู'),
    ('v','วี'),
    ('w','ดับเบิลยู'),
    ('x','เอ็กซ์'),
    ('y','วาย'),
    ('z','ซี')
]]


def num_to_thai(text):
    return re.sub(r'(?:\d+(?:,?\d+)?)+(?:\.\d+(?:,?\d+)?)?', lambda x: ''.join(num.NumberToTextThai(float(x.group(0).replace(',', '')))), text)

def latin_to_thai(text):
    for regex, replacement in _latin_to_thai:
        text = re.sub(regex, replacement, text)
    return text
