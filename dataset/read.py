import json
import os
import zipfile
from pathlib import Path

from dataset.core import AudioRecordMetadata, SampleEntry
from dataset.logger import get_logger

logger = get_logger(__name__)


def decode_json_bytes(json_bytes: bytes) -> json:
    decoded_json_string = json_bytes.decode('utf-8')
    formatted_json_string = format_json_string(decoded_json_string)
    return json.loads(formatted_json_string)


def format_json_string(manifest):
    return '[' + manifest.replace('}', '},')[:-2] + ']'  # -2 to take all except new line and comma


def read_dataset(input_dir: str, output_dir: str):
    examples = []
    file_idx = 0
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('zip'):
                examples += read_zip_entries(Path(root) / file, output_dir=output_dir, zipfile_idx=file_idx)
                file_idx += 1
    return len(examples), examples


def read_zip_entries(filepath: Path, output_dir, zipfile_idx: int):
    logger.info(f"Reading {filepath} zip entries...")
    samples = []
    with zipfile.ZipFile(str(filepath), 'r', compression=zipfile.ZIP_STORED) as zip_file:
        manifest = decode_json_bytes(zip_file.read("manifest.jsona"))
        for audio_idx, manifest_entry in enumerate(manifest):
            manifest_entry = AudioRecordMetadata(**manifest_entry)

            if '\n' in manifest_entry.zip_entry_name:
                print(manifest_entry)
                continue

            # this tool supports only WAV audio format datasets for now
            assert manifest_entry.zip_entry_name.endswith(".wav")

            audio_bytes = zip_file.read(manifest_entry.zip_entry_name)

            samples.append(SampleEntry.from_zip_sample_entry(audio_bytes=audio_bytes, metadata=manifest_entry,
                                                             output_dataset_dir=output_dir,
                                                             zipfile_idx=zipfile_idx, audio_idx=audio_idx))
    return samples
