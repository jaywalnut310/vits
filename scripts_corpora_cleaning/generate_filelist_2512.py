import os
from pathlib import Path
from sklearn.model_selection import train_test_split
import sys
import re
from nemo_text_processing.text_normalization.normalize import Normalizer


def contains_digits(s):
    # Return True if string contains any digit
    return re.search(r"\d", s) is not None


def load_perola():
    # we can just read all files from the perola corpus
    files = [
        "/media/4tbdrive/engines/vits/filelists/perola_audio_text_train_filelist.txt",
        "/media/4tbdrive/engines/vits/filelists/perola_audio_text_val_filelist.txt",
    ]
    data = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                data.append(line.split("|"))
    return data


def load_allapps():
    folder = Path(
        "/mnt/seagate8tbhdd/corpora/tts_ptbr_allapps/downsampled_silence_split_chunks/"
    )
    wav_files = list(folder.rglob("*.wav"))
    data = []
    for i in range(3):
        for file in wav_files:
            transcription_path = str(file).replace(".wav", ".txt")
            if not (Path(transcription_path).exists()):
                sys.exit(f"Transcription file {transcription_path} does not exist!")
            else:
                with open(transcription_path, "r", encoding="utf-8") as f:
                    text = f.read().strip().lower()
                    data.append([f"{file}", text])
    return data


def load_baiano():
    folder = Path("/mnt/seagate8tbhdd/corpora/TTS-Portuguese-Corpus/downsampled_wavs/")
    wav_files = list(folder.rglob("*.wav"))
    data = []
    for file in wav_files:
        transcription_path = str(file).replace(".wav", ".txt")
        if not (Path(transcription_path).exists()):
            sys.exit(f"Transcription file {transcription_path} does not exist!")
        else:
            with open(transcription_path, "r", encoding="utf-8") as f:
                text = f.read().strip().lower()
                data.append([f"{file}", text])
    return data


# first I read all files from all the corpora that we want to include
corpora_dirs = {}
corpora_dirs["1"] = load_perola()
corpora_dirs["3"] = load_baiano()
corpora_dirs["2"] = load_allapps()

for key in corpora_dirs:
    print(f"Corpus {key} has {len(corpora_dirs[key])} utterances.")

filelist = []
for key in corpora_dirs:
    for entry in corpora_dirs[key]:
        transcription = entry[1].lower()
        if contains_digits(transcription):
            print(f"Transcription contains digits: {transcription}")
        filelist.append(f"{entry[0]}|{key}|{transcription}")


train_set, val_set = train_test_split(filelist, test_size=0.2, random_state=42)
print(f"Final train set has {len(train_set)} utterances.")
print(f"Final val set has {len(val_set)} utterances.")
filelist_train = open(
    f"/media/4tbdrive/engines/vits/filelists/portuguese_mixed_corpora_train_2512.txt",
    "w+",
    encoding="utf-8",
)
for entry in train_set:
    filelist_train.write(entry.strip() + "\n")
filelist_train.close()

filelist_val = open(
    f"/media/4tbdrive/engines/vits/filelists/portuguese_mixed_corpora_val_2512.txt",
    "w+",
    encoding="utf-8",
)
for entry in val_set:
    filelist_val.write(entry.strip() + "\n")
filelist_val.close()
