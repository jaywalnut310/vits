import unittest

import nltk
from hamcrest import assert_that, equal_to, is_, contains_exactly


class TestSplitTextToSentences(unittest.TestCase):
    def test_text_split_given_multiple_sentences_in_text_when_splitting_then_sentences_split_correctly(self):
        # given
        text = "Taĩgi Lùcijus Anė́jus Sèneka (ketvir̃ti mẽtai priẽš Krìstų - šẽšiasdešimt penktì mẽtai põ " \
               "Krìstaus), kuriõ laiškaĩ čià pateikiamì, turė́jo filosòfinio láiško pìrmtakų ir̃ pavyzdžių̃, " \
               "gál galė́jusių pasiū́lyti šiókias tókias gairès (pávyzdžiui, šiám žánrui būdìngą " \
               "neoficialùmą, išsãkymo intymùmą), bèt sàvo laiškų̃ temãtiką ir̃ stilìstiką rašýtojas, " \
               "žìnoma, susikū́rė pàts. Visì jõ laiškaĩ pažénklinti didãktikos žénklu. Taĩ mókytojo " \
               "laiškaĩ. Jiẽ nėrà neĩ vadovė̃lis, neĩ pãskaitos, neĩ pamókslai, õ pókalbiai, " \
               "kupinì į́tampos, aistrõs, siẽkių įtìkinti ir̃ adresãtą, ir̃ skaitýtoją. Áutorius véngia " \
               "lòginio nuoseklùmo ir̃ sistemingùmo, retaĩ gvildẽna víeną tèmą, sukùrdamas tikróviškai " \
               "plaũkiančio, láiškui būdìngo pãšnekesio imitãciją. Rãmų pãsakojimą keĩčia kárštas " \
               "įrodinė́jimas, iròniją - pasipìktinimas. Pókalbiuose sù Lucìlijumi pribarstýta žavių̃ " \
               "kasdienýbės smùlkmenų (nuõ ìlgo gulė́jimo sulìpę, nebeišsivyniójantys knỹgų ritinė̃liai, " \
               "alỹvmedžių sodìnimas, kasdiẽnė mankštà, keliõnė, ligà, gumbúoti senų̃ platãnų kamíenai, " \
               "vỹnmedžių pérsodinimas, Ròmos pirčių̃ garsaĩ, aplankýtų dvarų̃ aprãšymai, bìčių darbaĩ ir̃ " \
               "panašiaĩ), tačiaũ Sènekos laiškaĩ nėrà reikalų̃ laiškaĩ. Jų̃ tìkslas - nè buĩtinio gyvẽnimo " \
               "naujíenų pranešìmas. Nórs áutorius nėrà taĩp nutólęs nuõ tikróvės, kaĩp tõs pačiõs " \
               "filosòfinės stoicìzmo kryptiẽs atstõvai Epiktètas ar̃ Márkas Aurèlijus, bèt kalbė́damas apiẽ " \
               "buitiẽs detalès jìs neištir̃psta kasdienýbėje, nė̃ valandė̃lei nepamir̃šta prisiimtõs mókytojo " \
               "pareigõs: Nereĩkia rãginti, nètgi patar̃ti, kàd akìs suvóktų spalvàs: báltą nuõ juodõs " \
               "atskir̃s niẽkam nenurodinė́jant. Õ síelai, príešingai, trū́ksta daugýbės pamókymų, " \
               "idañt pamatýtų, ką̃ privãlo nuveĩkti gyvẽnime (devýniasdešimt ketvir̃tas láiškas; " \
               "devynióliktas)."

        # when
        actual_sentences = nltk.sent_tokenize(text, language="finnish")

        # when
        expected_sentences = [
            "Taĩgi Lùcijus Anė́jus Sèneka (ketvir̃ti mẽtai priẽš Krìstų - šẽšiasdešimt penktì mẽtai põ "
            "Krìstaus), kuriõ laiškaĩ čià pateikiamì, turė́jo filosòfinio láiško pìrmtakų ir̃ pavyzdžių̃, "
            "gál galė́jusių pasiū́lyti šiókias tókias gairès (pávyzdžiui, šiám žánrui būdìngą neoficialùmą, "
            "išsãkymo intymùmą), bèt sàvo laiškų̃ temãtiką ir̃ stilìstiką rašýtojas, žìnoma, susikū́rė pàts.",

            "Visì jõ laiškaĩ pažénklinti didãktikos žénklu.",

            "Taĩ mókytojo laiškaĩ.",

            "Jiẽ nėrà neĩ vadovė̃lis, neĩ pãskaitos, neĩ pamókslai, õ pókalbiai, kupinì į́tampos, aistrõs, "
            "siẽkių įtìkinti ir̃ adresãtą, ir̃ skaitýtoją.",

            "Áutorius véngia lòginio nuoseklùmo ir̃ sistemingùmo, retaĩ gvildẽna víeną tèmą, sukùrdamas "
            "tikróviškai plaũkiančio, láiškui būdìngo pãšnekesio imitãciją.",

            "Rãmų pãsakojimą keĩčia kárštas įrodinė́jimas, iròniją - pasipìktinimas.",

            "Pókalbiuose sù Lucìlijumi pribarstýta žavių̃ kasdienýbės smùlkmenų (nuõ ìlgo gulė́jimo sulìpę, "
            "nebeišsivyniójantys knỹgų ritinė̃liai, alỹvmedžių sodìnimas, kasdiẽnė mankštà, keliõnė, ligà, "
            "gumbúoti senų̃ platãnų kamíenai, vỹnmedžių pérsodinimas, Ròmos pirčių̃ garsaĩ, aplankýtų dvarų̃ "
            "aprãšymai, bìčių darbaĩ ir̃ panašiaĩ), tačiaũ Sènekos laiškaĩ nėrà reikalų̃ laiškaĩ.",

            "Jų̃ tìkslas - nè buĩtinio gyvẽnimo naujíenų pranešìmas.",

            "Nórs áutorius nėrà taĩp nutólęs nuõ tikróvės, kaĩp tõs pačiõs filosòfinės stoicìzmo "
            "kryptiẽs atstõvai Epiktètas ar̃ Márkas Aurèlijus, bèt kalbė́damas apiẽ buitiẽs detalès jìs "
            "neištir̃psta kasdienýbėje, nė̃ valandė̃lei nepamir̃šta prisiimtõs mókytojo pareigõs: Nereĩkia "
            "rãginti, nètgi patar̃ti, kàd akìs suvóktų spalvàs: báltą nuõ juodõs atskir̃s niẽkam "
            "nenurodinė́jant.",

            "Õ síelai, príešingai, trū́ksta daugýbės pamókymų, idañt pamatýtų, ką̃ privãlo nuveĩkti "
            "gyvẽnime (devýniasdešimt ketvir̃tas láiškas; devynióliktas).",
        ]

        # then
        assert_that(len(expected_sentences), is_(equal_to(len(actual_sentences))))
        assert_that(expected_sentences, contains_exactly(*actual_sentences))
    def test_text_split_given_sentences_with_dialogue_when_splitting_then_sentences_split_correctly(self):
        # given
        text = "test.\n- test, - test. - test. test"

        # when
        actual_sentences = nltk.sent_tokenize(text, language="finnish")

        # when
        expected_sentences = ["test.",
                              "- test, - test.",
                              "- test.",
                              "- test"]

        # then
        assert_that(len(expected_sentences), is_(equal_to(len(actual_sentences))))
        assert_that(expected_sentences, contains_exactly(*actual_sentences))
