import re
from typing import List


def read_txt(txt_file_path) -> str:
    encodings = [
        'utf-8',
        'utf-16',
        'utf-8-sig',
        'cp1257',
        'iso8859_13',
    ]

    for encoding in encodings:
        try:
            with open(txt_file_path, mode='r', encoding=encoding) as file:
                text = file.read()
                text = text.strip()
                return text
        except (NotADirectoryError, FileNotFoundError) as e:
            raise Exception(f"Filepath error {e}")

    raise Exception("Could not read file given the encodings")


def read_book(filepath) -> List[str]:
    book_text = read_txt(filepath)
    book_text = re.sub(r"\n{2,}", "\n", book_text)
    return book_text.split('\n')
