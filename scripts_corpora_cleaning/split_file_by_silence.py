import os
from pathlib import Path
import wave
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
import argparse
import glob
from pathlib import Path


def split_by_silence(
    input_file,
    output_folder="/mnt/seagate8tbhdd/corpora/tts_ptbr_allapps/downsampled_silence_split_chunks/",
    min_silence_len=1000,
    silence_thresh=-40,
):
    """
    Split an audio file into chunks based on silence detection.

    Args:
        input_file (str): Path to input WAV file
        output_folder (str): Folder to save chunks
        min_silence_len (int): Minimum silence length in milliseconds (default: 1000ms = 1 second)
        silence_thresh (int): Silence threshold in dBFS (default: -40dBFS)

    Returns:
        list: List of chunk filenames
    """
    print(f"\nLoading audio file: {input_file}")

    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    print(f"Audio duration: {len(audio) / 1000:.2f} seconds")
    print(f"Detecting silence with threshold: {silence_thresh} dBFS")
    print(f"Minimum silence duration: {min_silence_len}ms")

    # Split on silence
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=100,  # Keep 100ms of silence at the beginning and end of each chunk
    )

    if not chunks:
        print("No silence detected. Saving entire file as single chunk.")
        chunks = [audio]

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save each chunk
    chunk_filenames = []
    print(f"\nSaving {len(chunks)} chunks...")

    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(output_folder, f"{input_file.stem}_{i+1:03d}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_filenames.append(chunk_filename)
        print(f"  Saved chunk {i+1}: {chunk_filename} ({len(chunk) / 1000:.2f}s)")

    return chunk_filenames


path = "/mnt/seagate8tbhdd/corpora/tts_ptbr_allapps/"
path = Path(os.path.join(path))
wav_files = list(path.rglob("*.wav"))
for file in wav_files:
    split_by_silence(file)
