import os
import re
from nemo_text_processing.text_normalization.normalize import Normalizer

normalizer = Normalizer(lang="en", cache_dir="~/.cache/nemo")

folder = "/media/4tbdrive/engines/vits/allison_corpora/data/chunks/"  # Change to your target folder


def is_only_letters(s):
    # Return True if string contains any digit
    return re.search(r"\d", s) is not None


for filename in os.listdir(folder):
    if filename.endswith(".txt"):
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            text = f.read().strip().lower()
            if is_only_letters(text):
                full_path = os.path.join(folder, filename)
                print(f"{full_path}|{text}")
