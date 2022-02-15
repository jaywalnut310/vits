import json
import os
import re
import string
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from unidecode import unidecode

from dataset.logger import get_logger
from dataset.read import read_zip_entries

logger = get_logger(__name__)


if __name__ == '__main__':
    input_zipped_dataset_dir = "/media/arnas/SSD Disk/inovoice/zipped/nijole_lipeikaite_voice_zips"
    # input_zipped_dataset_dir = "/media/arnas/SSD Disk/inovoice/unzipped/audiobooks"
    output_dir = "/media/arnas/SSD Disk/inovoice/unzipped/audiobooks_formatted"
    # dataset_names = ["algis_ramanauskas_voice_zips", "nijole_lipeikaite_voice_zips"]

    examples = []
    file_idx = 0
    for root, dirs, files in os.walk(input_zipped_dataset_dir):
        for file in files:
            examples += read_zip_entries(Path(root) / file, output_dir, file_idx)
            file_idx += 1

    logger.info("Writing dataset files...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    examples = sorted(examples, key=lambda example: example.duration, reverse=True)
    examples_df = pd.DataFrame([example.duration for example in examples], columns=['duration'])
    sns.displot(examples_df, x="duration")
    plt.show()
    for example in examples[:100]:
        print(f"len: {example.duration}, path: {example.filepath}")
