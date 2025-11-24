import os
import re
from nemo_text_processing.text_normalization.normalize import Normalizer
from pathlib import Path
from sklearn.model_selection import train_test_split
import asyncio
from fast_langdetect import (
    detect,
    detect_multilingual,
    LangDetector,
    LangDetectConfig,
    DetectError,
)
import sqlite3

conn = sqlite3.connect(
    "/media/4tbdrive/engines/vits/allison_corpora/data/files.db"
)  # Connects to a file-based database
cursor = conn.cursor()

normalizer = Normalizer(lang="en", cache_dir="~/.cache/nemo", input_case="lower_cased")
folder = "/media/4tbdrive/engines/vits/allison_corpora/data/chunks/"  # Change to your target folder

lines = []
max_length = 1000  # seconds
min_length = 2  # seconds


def contains_digits(s):
    # Return True if string contains any digit
    return re.search(r"\d", s) is not None


with open(
    "/media/4tbdrive/engines/vits/allison_corpora/data/lenghts.txt",
    "r",
    encoding="utf-8",
) as f:
    lines = f.readlines()

# entry in the format
# DUMMY1/LJ045-0096.wav|Mrs. De Mohrenschildt thought that Oswald,
train_val_list = []
test_list = []
total = 0
skipped = []


async def process_chunks():
    semaphore = asyncio.Semaphore(20)  # Limit concurrency (tune as needed)
    batch_size = 200  # number of jobs to run in parallel

    async def process_file(line):
        async with semaphore:
            k, v = line.split(",")[0].strip(), float(line.split(",")[1].strip())
            # read transcription
            filename = k.replace(".wav", ".txt")
            transcription = ""
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                transcription = f.read().strip().lower()
                lang = detect(transcription, low_memory=False)
                cursor.execute(
                    "UPDATE files SET transcription = ?, language = ? WHERE path = ?",
                    (transcription, lang["lang"], k),
                )

                # we skip if the text is not english
                if contains_digits(transcription):
                    transcription = normalizer.normalize(transcription)
                    if contains_digits(transcription):
                        print(f"Skipping non-normalized text: {transcription}")
                        skipped.append(f"{k}|{transcription}")
                        return

            if lang["lang"] != "en":
                print(f"Skipping non-English text: {transcription}")
                skipped.append(f"{k}|{transcription}")
                return

            if v < min_length:
                print(f"Skipping too short audio: {k} with length {v}")
                skipped.append(f"{k}|{transcription}")
                return

            file_list_entry = f"DUMMY/{Path(k).name}|{transcription}"
            if v > max_length:
                test_list.append(file_list_entry)
                return

            train_val_list.append(file_list_entry)

    for i in range(0, len(lines), batch_size):
        batch = lines[i : int(i + (batch_size))]
        tasks = []
        for entry in batch:
            tasks.append(process_file(entry))
        await asyncio.gather(*tasks)

    train_set, val_set = train_test_split(
        train_val_list, test_size=0.1, random_state=42
    )

    filelist_test = open(
        f"/media/4tbdrive/engines/vits/filelists/allison_full_test_{max_length}.txt",
        "w",
        encoding="utf-8",
    )
    for entry in test_list:
        filelist_test.write(entry + "\n")

    filelist_train = open(
        f"/media/4tbdrive/engines/vits/filelists/allison_full_train_{max_length}.txt",
        "w",
        encoding="utf-8",
    )

    for entry in train_set:
        filelist_train.write(entry + "\n")

    filelist_val = open(
        f"/media/4tbdrive/engines/vits/filelists/allison_full_val_{max_length}.txt",
        "w",
        encoding="utf-8",
    )

    for entry in val_set:
        filelist_val.write(entry + "\n")

    skipped_file = open(
        f"/media/4tbdrive/engines/vits/filelists/allison_skipped_file_{max_length}.txt",
        "w",
        encoding="utf-8",
    )

    for entry in skipped:
        skipped_file.write(entry + "\n")

    conn.commit()
    conn.close()


asyncio.run(process_chunks())

# if is_only_letters(text):
#    full_path = os.path.join(folder, filename)
#    print(f"{full_path}|{text}")
#    chunk = Chunk()
#    chunk.audio_path = full_path
#    chunk.transcription = text
