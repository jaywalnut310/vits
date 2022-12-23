import itertools
import math
import sys
from pathlib import Path

from src.logger import get_logger
from src.zipper.phonemizer import phonemize_

logger = get_logger(__name__)


# def phonemize_dataset(dataset, language):
#     phonemized_data = []
#     dataset_len = len(dataset)
#     for idx, (filepath, text) in enumerate(dataset):
#         logger.info(f"Phonemizing utterance {idx}/{dataset_len}: {text.strip()}")
#         phonemized_text = phonemize_(text, language=language)
#         phonemized_data.append('|'.join([filepath, phonemized_text]))
#     return phonemized_data


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    Source: https://stackoverflow.com/a/312464
    """

    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def phonemize_with_logging(chunk, language, idx, number_of_chunks):
    logger.info(f"Phonemizing chunk #{idx}/{number_of_chunks}")
    return phonemize_(chunk, language)


if __name__ == '__main__':
    dataset_language = 'en-us'  # 'lt'
    input_dir = "/home/aai-labs/inovoice/repos/vits/files/filelists"
    name = 'openslr_9017'
    filenames = [
        f"{name}_train_filelist.txt",
        f"{name}_val_filelist.txt",
        f"{name}_test_filelist.txt"
    ]
    chunk_size = 150 # reduce if RecursionError is thrown

    for filename in filenames:
        logger.info(f"Loading filelist {filename}")
        output_filename = f"{Path(filename).stem}_phonemized.txt"

        with open(Path(input_dir) / filename, mode='r') as f:
            filelist_lines = f.read().strip().split('\n')

        dataset_filepaths, dataset_texts = map(list, zip(*[line.split('|') for line in filelist_lines]))

        # Split the dataset into chunks of `chunk_size` elements
        # Note: without chunking, phonemizer raises
        #   `RecursionError: maximum recursion depth exceeded while calling a Python object`
        nchunks = math.ceil(len(dataset_texts) / chunk_size)
        dataset_text_chunks = chunks(dataset_texts, chunk_size)

        logger.info(f"Phonemizing {filename}...")
        phonemized_text_chunks = [phonemize_with_logging(text_chunk, dataset_language, idx, nchunks)
                                  for idx, text_chunk in enumerate(dataset_text_chunks, start=1)]
        phonemized_texts = list(itertools.chain.from_iterable(phonemized_text_chunks))

        if len(dataset_filepaths) != len(phonemized_texts):
            raise ValueError(f"Unequal sizes of lists `dataset_filepaths` ({len(dataset_filepaths)}) "
                             f"and `phonemized_texts` ({len(phonemized_texts)})")

        phonemized_dataset = zip(dataset_filepaths, phonemized_texts)

        logger.info(f"Writing dataset to {output_filename}")
        with open(Path(input_dir) / output_filename, mode='w') as f:
            f.write('\n'.join(['|'.join(pair) for pair in phonemized_dataset]))
