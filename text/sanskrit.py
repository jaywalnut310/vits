import re
from indic_transliteration import sanscript


# List of (iast, ipa) pairs:
_iast_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('a', 'ə'),
    ('ā', 'aː'),
    ('ī', 'iː'),
    ('ū', 'uː'),
    ('ṛ', 'ɹ`'),
    ('ṝ', 'ɹ`ː'),
    ('ḷ', 'l`'),
    ('ḹ', 'l`ː'),
    ('e', 'eː'),
    ('o', 'oː'),
    ('k', 'k⁼'),
    ('k⁼h', 'kʰ'),
    ('g', 'g⁼'),
    ('g⁼h', 'gʰ'),
    ('ṅ', 'ŋ'),
    ('c', 'ʧ⁼'),
    ('ʧ⁼h', 'ʧʰ'),
    ('j', 'ʥ⁼'),
    ('ʥ⁼h', 'ʥʰ'),
    ('ñ', 'n^'),
    ('ṭ', 't`⁼'),
    ('t`⁼h', 't`ʰ'),
    ('ḍ', 'd`⁼'),
    ('d`⁼h', 'd`ʰ'),
    ('ṇ', 'n`'),
    ('t', 't⁼'),
    ('t⁼h', 'tʰ'),
    ('d', 'd⁼'),
    ('d⁼h', 'dʰ'),
    ('p', 'p⁼'),
    ('p⁼h', 'pʰ'),
    ('b', 'b⁼'),
    ('b⁼h', 'bʰ'),
    ('y', 'j'),
    ('ś', 'ʃ'),
    ('ṣ', 's`'),
    ('r', 'ɾ'),
    ('l̤', 'l`'),
    ('h', 'ɦ'),
    ("'", ''),
    ('~', '^'),
    ('ṃ', '^')
]]


def devanagari_to_ipa(text):
    text = text.replace('ॐ', 'ओम्')
    text = re.sub(r'\s*।\s*$', '.', text)
    text = re.sub(r'\s*।\s*', ', ', text)
    text = re.sub(r'\s*॥', '.', text)
    text = sanscript.transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)
    for regex, replacement in _iast_to_ipa:
        text = re.sub(regex, replacement, text)
    text = re.sub('(.)[`ː]*ḥ', lambda x: x.group(0)
                  [:-1]+'h'+x.group(1)+'*', text)
    return text
