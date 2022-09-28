""" Based on https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
'''

# Non-stressed symbols:
_pad = '_'
_punctuation = ';:,.!?¡¿—…"«»“” '
_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
_letters_ipa = "ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘'̩'ᵻ"

# Stressed symbols:
# _stressed_letters = 'abcdefghijklmnopqrstuvwxyząčęėįšųūž'
_stressed_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzĄČĘĖĮŠŲŪŽąčęėįšųūž'
_stressed_punctuation = '";:,.!?—-\'"() '
_accents = u'\u0300\u0301\u0303'


def get_vocabulary(language: str):
    if language == 'en':
        symbols = [_pad] + list(_punctuation) + list(_letters) + list(_letters_ipa)

        symbol_to_id = {s: i for i, s in enumerate(symbols)}
        id_to_symbol = {i: s for i, s in enumerate(symbols)}

        return symbols, symbol_to_id, id_to_symbol
    elif language == 'lt':
        stressed_symbols = [_pad] + list(_stressed_punctuation) + list(_stressed_letters) + list(_accents)

        symbol_to_id = {s: i for i, s in enumerate(stressed_symbols)}
        id_to_symbol = {i: s for i, s in enumerate(stressed_symbols)}

        return stressed_symbols, symbol_to_id, id_to_symbol
    else:
        raise NotImplementedError

# # remove uppercase letters from vocabulary
# to_delete = dict()
# for symbol, idx in symbol_to_id.items():
#     if symbol.isupper():
#         to_delete[symbol] = idx
# for symbol, idx in to_delete.items():
#     del symbol_to_id[symbol]
#     del id_to_symbol[idx]
