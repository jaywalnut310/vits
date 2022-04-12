from dataclasses import replace
from io import BytesIO
from pathlib import Path

from pydub import AudioSegment

from libs.dataset.batch import index_entries
from libs.dataset.core import SampleEntry
from logger import get_logger
from libs.dataset.phonemizer import phonemize_entry
from libs.dataset.pipeline import does_not_have_numbers, waveform_not_longer_than, waveform_not_shorter_than
from libs.dataset.read import read_dataset
from libs.dataset.write import write_audio, write_filelists_entry

logger = get_logger(__name__)


def example_does_not_exist(entry: SampleEntry):
    return not Path(entry.filepath).is_file()


def set_sample_rate_if_not(sample_rate: int):
    def step(entry: SampleEntry) -> SampleEntry:
        if entry.sample_rate == sample_rate:
            return entry

        return replace(entry, audio_bytes=set_sample_rate(entry, sample_rate), sample_rate=sample_rate)

    return step


def set_sample_rate(entry: SampleEntry, sample_rate) -> bytes:
    logger.info(f"Setting sample rate of {entry.filepath} from {entry.sample_rate} to {sample_rate}")
    audio = AudioSegment.from_wav(BytesIO(entry.audio_bytes))
    audio = audio.set_frame_rate(sample_rate)
    audio_bytes = BytesIO()
    audio.export(audio_bytes, format='wav', parameters=['-ar', f"{sample_rate}"])
    return audio_bytes.getvalue()


def phonemize_indexed_entry_with_logging(dataset_len: int):
    def step(indexed_entry):
        idx, entry = indexed_entry
        logger.info(f"Phonemizing utterance {idx}/{dataset_len}: {entry.text.strip()}")
        return idx, phonemize_entry(entry)

    return step


def write_indexed_entry(indexed_entry):
    idx, entry = indexed_entry
    return idx, write_audio(entry)


if __name__ == '__main__':
    # configs...
    input_zipped_dataset_dir = "/media/arnas/SSD Disk/inovoice/zipped/stressed/paulius_ciziniauskas_voice_zips"
    dataset_output_dir = "/media/arnas/SSD Disk/inovoice/unzipped/vits_audiobooks/paulius_ciziniauskas_stressed"
    filelists_output_dir = "/media/arnas/SSD Disk/uni/semester_3/master_thesis/repos/vits/filelists"
    Path(dataset_output_dir).mkdir(parents=True, exist_ok=True)
    Path(filelists_output_dir).mkdir(parents=True, exist_ok=True)
    name = "paulius_stressed"
    min_audio_len = 0.5
    max_audio_len = 13.00
    train_split = 0.98
    val_test_split = (1 - train_split) / 2
    sr = 22050  # sample rate
    phonemize_dataset = False

    logger.info("Reading dataset...")
    full_dataset_len, examples = read_dataset(input_zipped_dataset_dir, dataset_output_dir)
    logger.info("Processing dataset...")
    examples = map(set_sample_rate_if_not(sr), examples)
    examples = filter(does_not_have_numbers, examples)
    examples = filter(waveform_not_shorter_than(min_audio_len), examples)
    examples = filter(waveform_not_longer_than(max_audio_len), examples)
    examples = list(examples)
    dataset_len = len(examples)
    logger.info(f"Full dataset size: {full_dataset_len}; Filtered out {full_dataset_len - dataset_len} examples")

    examples = filter(example_does_not_exist, examples)
    examples = list(examples)
    current_idx = dataset_len - len(examples)
    logger.info(f"Already existing examples count: {current_idx}/{dataset_len}")

    examples = map(index_entries(current_idx), examples)
    if phonemize_dataset:
        examples = map(phonemize_indexed_entry_with_logging(dataset_len), examples)
    examples = map(write_indexed_entry, examples)
    examples = map(
        write_filelists_entry(dataset_len, current_idx, train_split, val_test_split, name, filelists_output_dir),
        examples)

    for idx, example in examples:
        logger.info(f"Done processing {example.filepath}")

    logger.info("Dataset processing completed...")
