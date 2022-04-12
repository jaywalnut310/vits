from pathlib import Path

from libs.file import read_txt


def read_filelist_texts(filepath):
    contents = read_txt(filepath)
    lines = contents.split(('\n'))
    contents = [line.split('|')[1] for line in lines]
    return '\n'.join(contents)


if __name__ == '__main__':
    filepath = Path("/libs/dataset/tools/giedrius_arbaciauskas_stressed_44100khz_val_filelist.txt")
    texts = read_filelist_texts(filepath)

    vocab = set(texts)
    vocab = sorted(vocab)

    print(f"Vocabulary:\n{vocab}")
    print(f"Vocabulary size:\n{len(vocab)}")
