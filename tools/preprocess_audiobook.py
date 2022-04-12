from pathlib import Path

from libs.dataset.pipeline import replace_oov, replace_letter_to_sound, test_replace_letter_to_sound
from libs.file import read_txt

if __name__ == '__main__':
    in_filepath = Path("/media/arnas/SSD Disk/inovoice/text_data/synthesis-audiobooks/processed/Kur vasara amžina.txt")
    out_filepath = Path(
        "/media/arnas/SSD Disk/inovoice/text_data/synthesis-audiobooks/processed/Kur vasara amžina_processed.txt")

    test_replace_letter_to_sound()

    text = read_txt(in_filepath)
    lines = text.split('\n')
    lines = [replace_oov(line) for line in lines]
    lines = [replace_letter_to_sound(line) for line in lines]
    contents = '\n'.join(lines)

    with open(out_filepath, mode='w', encoding='utf-8') as f:
        f.write(contents)
