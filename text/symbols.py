""" from https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
'''

# japanese_cleaners
_pad        = '_'
_punctuation = ',.!?-'
_letters = 'AEINOQUabdefghijkmnoprstuvwyzʃʧ↓↑ '


'''# japanese_cleaners2
_pad        = '_'
_punctuation = ',.!?-'
_letters = 'AEINOQUabdefghijkmnoprstuvwyzʃʧʦ↓↑ '
'''

'''# korean_cleaners
_pad        = '_'
_punctuation = ',.!?…~'
_letters = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄲㄸㅃㅆㅉㅏㅓㅗㅜㅡㅣㅐㅔ '
'''

# Export all symbols:
symbols = [_pad] + list(_punctuation) + list(_letters)

# Special symbol ids
SPACE_ID = symbols.index(" ")
