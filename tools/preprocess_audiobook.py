from pathlib import Path

from src.file import read_txt
from src.zipper.pipeline import replace_oov, replace_letter_to_sound

if __name__ == '__main__':
    in_filepath = Path("/media/arnas/SSD Disk/inovoice/text_data/synthesis-audiobooks/processed/Kur vasara amžina.txt")
    out_filepath = Path(
        "/media/arnas/SSD Disk/inovoice/text_data/synthesis-audiobooks/processed/Kur vasara amžina_processed.txt")

    text = read_txt(in_filepath)
    lines = text.split('\n')
    lines = [replace_oov(line) for line in lines]
    lines = [replace_letter_to_sound(line) for line in lines]
    contents = '\n'.join(lines)

    with open(out_filepath, mode='w', encoding='utf-8') as f:
        f.write(contents)
