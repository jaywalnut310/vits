from pathlib import Path

from phonemizer import phonemize

from src.logger import get_logger

logger = get_logger(__name__)


def phonemize_dataset(dataset):
    phonemized_dataset = []
    dataset_len = len(dataset)
    for idx, (filepath, text) in enumerate(dataset):
        print(f"Phonemizing utterance {idx}/{dataset_len}: {text.strip()}")
        phonemized_text = phonemize(text, language='lt', backend='espeak', strip=True)
        phonemized_dataset.append('|'.join([filepath, phonemized_text]))
    return phonemized_dataset


if __name__ == '__main__':

    input_dir = "/media/arnas/SSD Disk/uni/semester_3/master_thesis/repos/vits/filelists"
    name = 'paulius'
    filenames = [
        f"{name}_train_filelist.txt",
        f"{name}_val_filelist.txt",
        f"{name}_test_filelist.txt"
    ]
    for filename in filenames:
        print(f"Loading filelist {filename}")
        dataset = [tuple(example_line.split('|')) for example_line in
                   open(str(Path(input_dir) / filename), mode='r').readlines()]

        output_filename = f"{filename.split('.')[0]}_phonemized.txt"
        print(f"Writing dataset to {output_filename}")
        phonemized_dataset = phonemize_dataset(dataset)
        open(Path(input_dir) / output_filename, mode='w').write('\n'.join(phonemized_dataset))
