from pathlib import Path

from dataset.core import SampleEntry
from dataset.logger import get_logger

logger = get_logger(__name__)


def write_audio(entry: SampleEntry):
    with open(entry.filepath, mode='wb') as audio_file:
        audio_file.write(entry.audio_bytes)

    return entry


def write_filelists(entries, train_split, val_test_split, dataset_name: str, output_dir):
    dataset = [entry.as_string() for entry in entries]

    train_set, val_set, test_set = split_(dataset, train_split, val_test_split)

    write_filelist(output_dir, f"{dataset_name}_train_filelist.txt", train_set)
    write_filelist(output_dir, f"{dataset_name}_val_filelist.txt", val_set)
    write_filelist(output_dir, f"{dataset_name}_test_filelist.txt", test_set)


def split_(dataset, train_split, val_test_split):
    dataset_len = len(dataset)
    training_example_count = int(dataset_len * train_split)
    val_test_example_count = int(dataset_len * val_test_split)

    train_set = dataset[:training_example_count]
    val_set = dataset[training_example_count:training_example_count + val_test_example_count]
    test_set = dataset[training_example_count + val_test_example_count:dataset_len]

    return train_set, val_set, test_set


def write_filelist(output_dir, filename, data_lines):
    open(Path(output_dir) / filename, mode='w').write('\n'.join(data_lines))


def write_filelists_entry(total_dataset_len, current_dataset_entry_idx,
                          train_split, val_test_split, dataset_name, output_dir):
    # TODO: fix a bug here (dataset is split incorrectly)
    training_example_count = int(total_dataset_len * train_split)
    val_test_example_count = int(total_dataset_len * val_test_split)

    train_filelist_name = f"{dataset_name}_train_filelist.txt"
    val_filelist_name = f"{dataset_name}_val_filelist.txt"
    test_filelist_name = f"{dataset_name}_test_filelist.txt"
    print('CALLING write_filelists_entry')

    def step(indexed_entry):
        idx, entry = indexed_entry
        current_idx = idx + current_dataset_entry_idx
        logger.info(f"Writing filelist entry {current_idx}/{total_dataset_len}: {entry.text.strip()}")

        if current_idx < training_example_count:
            filelist_name = train_filelist_name
        elif current_idx < (training_example_count + val_test_example_count):
            filelist_name = val_filelist_name
        else:
            filelist_name = test_filelist_name

        with open(Path(output_dir) / filelist_name, mode='a', encoding='utf-8') as f:
            f.write(f"{entry.as_csv_string()}\n")

        return indexed_entry

    return step
