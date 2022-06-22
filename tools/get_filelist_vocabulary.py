from pathlib import Path

from src.file import read_txt


def read_filelist_texts(filepath):
    contents = read_txt(filepath)
    lines = contents.split('\n')
    contents = [line.split('|')[1] for line in lines]
    return '\n'.join(contents)


if __name__ == '__main__':
    filepath = Path("/media/arnas/SSD Disk/uni/semester_4/thesis-files/mos/lt_synthesizer_survey/filelist.txt")
    texts = read_filelist_texts(filepath)

    vocab = set(texts)
    vocab = sorted(vocab)

    print(f"Vocabulary:\n{vocab}")
    print(f"Vocabulary size:\n{len(vocab)}")
    print(texts)
