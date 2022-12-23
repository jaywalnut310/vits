import re
from typing import List

sentence_end_pattern = '[.?!]+[\'"]?'


def split_lines_to_sentences(book_lines: List[str]) -> List[List[str]]:
    s_sentences = []
    for line in book_lines:
        sentence_ends = [e for e in re.finditer(sentence_end_pattern, line)]
        if len(sentence_ends) == 0:
            s_sentences.append([line])
            continue

        i = 0
        sentences = []
        for e in sentence_ends:
            sentences.append(line[i:e.end()])
            i = e.end() + 1
        s_sentences.append(sentences)
    return s_sentences


if __name__ == '__main__':
    assert split_lines_to_sentences(
        [
            '- Taĩ bùvo labaĩ seniaĩ. '
            'Mū́sų prótėviai jójo, jójo ìš kažiñ kur̃ ir̃ prijójo šìtą žẽmę. '
            'õ čià - kalnaĩ añt kalnų̃, ėė̃ añt tų̃ kalnų̃ kalnaĩ ir̃ mažì kalnẽliai... '
            '"Čià mẽs lìksim, čià bùs Lietuvà", - apsìdžiaugė jiẽ. '
            'Bèt jaunì výrai taĩp ilgaĩ bùvo klajóję, kàd nebegalė́jo sustóti, jíems baĩsiai rūpė́jo, kàs teñ toliaũ, ùž jū́ros... '
            'Taĩgi jiẽ pasistãtė laivùs, pérplaukė jū́rą, rãdo daũg salų̃ ir̃ uolė́tą krãštą, pavadìno jį̃ Švèdija ir̃ palìko teñ sàvo móteris.']) == [
               [
                   '- Taĩ bùvo labaĩ seniaĩ.',
                   'Mū́sų prótėviai jójo, jójo ìš kažiñ kur̃ ir̃ prijójo šìtą žẽmę.',
                   'õ čià - kalnaĩ añt kalnų̃, ėė̃ añt tų̃ kalnų̃ kalnaĩ ir̃ mažì kalnẽliai...',
                   '"Čià mẽs lìksim, čià bùs Lietuvà", - apsìdžiaugė jiẽ.',
                   'Bèt jaunì výrai taĩp ilgaĩ bùvo klajóję, kàd nebegalė́jo sustóti, jíems baĩsiai rūpė́jo, kàs teñ toliaũ, ùž jū́ros...',
                   'Taĩgi jiẽ pasistãtė laivùs, pérplaukė jū́rą, rãdo daũg salų̃ ir̃ uolė́tą krãštą, pavadìno jį̃ Švèdija ir̃ palìko teñ sàvo móteris.']]
