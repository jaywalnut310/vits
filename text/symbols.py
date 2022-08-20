""" from https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
'''
_numbers = '0123456789'
_pad        = '_'
_punctuation = ';:,.!?¡¿—…"«»“” '
_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
_letters_ipa = "ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘'̩'ᵻ"
_py = ['sh', 'uo1', 'i3', 'ai2', 'i4', 'en2', 'en4', 'zh', 'eng3', 'ing4', 'i1', 'ia4', 'uo3', 'en', 'u2', 'e3', 'i2', 'üan2', 'ong1', 'ü2', 'u4', 'iong4', 'ai4', 'uang1', 'ie3', 'uei1', 'an2', 'iang3', 'e4', 'üe4', 'an4', 'ian4', 'iou3', 'uei4', 'ei2', 'ua4', 'iou4', 'ch', 'u1', 'a1', 'iong1', 'ian3', 'ou1', 'ong4', 'ü4', 'ian1', 'iang4', 'uo4', 'ü3', 'eng2', 'e2', 'ou4', 'an', 'ao3', 'ua1', 'in3', 'ou2', 'ie4', 'eng1', 'ou3', 'an3', 'er2', 'ai1', 'ie2', 'ing3', 'iou2', 'o1', 'ong3', 'an1', 'in4', 'ang1', 'ing2', 'ao4', 'iao4', 'a4', 'ing1', 'a3', 'ong2', 'iao1', 'in1', 'en3', 'uan2', 'uai4', 'ian2', 'e1', 'uei2', 'ang4', 'uang4', 'eng4', 'uan3', 'ai', 'iang', 'üe2', 'iao3', 'ei3', 'iou1', 'üan4', 'uan4', 'ou', 'o2', 'ei4', 'ei', 'ia', 'u3', 'ia1', 'en1', 'uan1', 'in2', 'ing', 'ün2', 'ie1', 'uo2', 'iang1', 'ei1', 'ang2', 'iao2', 'üan3', 'a2', 'ao1', 'iou', 'uen1', 'iang2', 'ang3', 'ua3', 'uen2', 'ie', 'ai3', 'uo', 'iong2', 'uen4', 'uang3', 'o4', 'ang', 'uei3', 'üan1', 'uang', 'ua', 'ian', 'uang2', 'er3', 'eng', 'ü1', 'ao2', 'ün1', 'uan', 'üe1', 'uen3', 'ia3', 'er4', 'uai2', 'er', 'ua2', 'uai3', 'ao', 'uen', 'ün4', 'in', 'iong3', 'ong', 'ün3', 'ün', 'ia2', 'uai1', 'üe3', 'iao', 'o3', 'uai', 'ueng1', 'uei', 'ü', 'iong']

_zhpunc = '！，、。？—…“”《》：+（）「」~；·・'

# Export all symbols:
symbols = [_pad] + list(_punctuation) + list(_letters) + list(_letters_ipa) + list(_numbers) + list(_zhpunc) + _py

# Special symbol ids
SPACE_ID = symbols.index(" ")
