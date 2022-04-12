from pathlib import Path

from libs.file import read_txt
from logger import get_logger

if __name__ == '__main__':
    in_filepath = Path("/media/arnas/SSD Disk/inovoice/text_data/synthesis-audiobooks/processed/Kur_vasara_amžina_processed.txt")
    out_filepath = Path(
        "/media/arnas/SSD Disk/inovoice/text_data/synthesis-audiobooks/processed/Kur vasara amžina_processed.txt")
    logger = get_logger(__name__)
    accents = ['\u0300', '\u0301', '\u0303']

    text = read_txt(in_filepath)
    lines = text.split('\n')
    unstressed_words = []
    for idx, line in enumerate(lines, start=1):
        for word in line.split(' '):
            if len(word) > 1 and not any(accent in word for accent in accents):
                logger.info(f"Unstressed word `{word}` in line #{idx}, sentence: {line}")
                unstressed_words.append(word)
    logger.info(f"Total unstressed_words: {len(unstressed_words)}")
