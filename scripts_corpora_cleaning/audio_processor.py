import os
import wave
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
import argparse
import glob


def concatenate_wav_files(input_folder, output_file="concatenated.wav"):
    """
    Concatenate all WAV files in a folder into a single WAV file.

    Args:
        input_folder (str): Path to folder containing WAV files
        output_file (str): Output filename for concatenated file

    Returns:
        str: Path to the concatenated file
    """
    print("Scanning for WAV files...")

    # Get all WAV files in the folder
    wav_files = glob.glob(os.path.join(input_folder, "**", "*.wav"), recursive=True)
    wav_files.extend(
        glob.glob(os.path.join(input_folder, "**", "*.WAV"), recursive=True)
    )

    if not wav_files:
        raise ValueError(f"No WAV files found in {input_folder}")

    # Sort files to ensure consistent order
    wav_files.sort()

    print(f"Found {len(wav_files)} WAV files:")

    # Load first file to get audio parameters
    first_audio = AudioSegment.from_wav(wav_files[0])
    concatenated = first_audio

    # Concatenate all other files
    print("\nConcatenating files...")
    for i, wav_file in enumerate(wav_files[1:], 1):
        try:
            audio = AudioSegment.from_wav(wav_file)
            concatenated += audio
            print(f"  Added file {i+1}/{len(wav_files)}")
        except Exception as e:
            print(f"  Error processing {wav_file}: {e}")
            continue

    print("\nConverting to 22050 Hz...")
    concatenated = concatenated.set_frame_rate(22050)

    # Export concatenated file
    concatenated.export(output_file, format="wav")
    print(f"\nConcatenated file saved as: {output_file}")
    print(f"Total duration: {len(concatenated) / 1000:.2f} seconds")

    return output_file


def split_by_silence(
    input_file, output_folder="chunks", min_silence_len=1000, silence_thresh=-40
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
        chunk_filename = os.path.join(output_folder, f"chunk_{i+1:03d}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_filenames.append(chunk_filename)
        print(f"  Saved chunk {i+1}: {chunk_filename} ({len(chunk) / 1000:.2f}s)")

    return chunk_filenames


def analyze_audio_levels(input_file, sample_duration=10):
    """
    Analyze audio levels to help determine optimal silence threshold.

    Args:
        input_file (str): Path to input WAV file
        sample_duration (int): Duration in seconds to analyze
    """
    print(f"\nAnalyzing audio levels in {input_file}...")

    audio = AudioSegment.from_wav(input_file)

    # Take a sample from the middle of the file
    start_time = max(0, (len(audio) // 2) - (sample_duration * 1000 // 2))
    end_time = min(len(audio), start_time + (sample_duration * 1000))
    sample = audio[start_time:end_time]

    # Calculate RMS (Root Mean Square) - a measure of loudness
    rms = sample.rms

    # Convert to dBFS (decibels relative to full scale)
    if rms > 0:
        dbfs = 20 * np.log10(rms / sample.max_possible_amplitude)
    else:
        dbfs = -np.inf

    print(f"Sample RMS: {rms}")
    print(f"Sample dBFS: {dbfs:.2f}")
    print(f"Suggested silence threshold: {dbfs - 10:.2f} to {dbfs - 20:.2f} dBFS")


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate WAV files and split by silence"
    )
    parser.add_argument(
        "--input_folder", "-i", help="Folder containing WAV files to concatenate"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="concatenated.wav",
        help="Output filename for concatenated file",
    )
    parser.add_argument(
        "--chunks-folder", "-c", default="chunks", help="Folder to save split chunks"
    )
    parser.add_argument(
        "--min-silence",
        "-s",
        type=int,
        default=1000,
        help="Minimum silence length in milliseconds (default: 1000)",
    )
    parser.add_argument(
        "--silence-thresh",
        "-t",
        type=int,
        default=-40,
        help="Silence threshold in dBFS (default: -40)",
    )
    parser.add_argument(
        "--analyze-only",
        "-a",
        action="store_true",
        help="Only analyze audio levels without processing",
    )
    parser.add_argument(
        "--skip-concat",
        action="store_true",
        help="Skip concatenation and split existing file",
    )

    args = parser.parse_args()

    try:
        # Import required libraries
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence
        except ImportError:
            print("Error: pydub library not found.")
            print("Please install it with: pip install pydub")
            print(
                "You may also need to install ffmpeg for additional audio format support."
            )
            return

        if args.analyze_only:
            # Just analyze the audio levels
            if os.path.isfile(args.input_folder):
                analyze_audio_levels(args.input_folder)
            else:
                print(f"File not found: {args.input_folder}")
            return

        if not args.skip_concat:
            # Step 1: Concatenate all WAV files
            concatenated_file = concatenate_wav_files(args.input_folder, args.output)
        else:
            concatenated_file = args.output
            if not os.path.isfile(concatenated_file):
                print(f"Error: File {concatenated_file} not found")
                return

        # Step 2: Analyze audio levels (optional)
        analyze_audio_levels(concatenated_file)

        # Step 3: Split by silence
        chunk_files = split_by_silence(
            concatenated_file, args.chunks_folder, args.min_silence, args.silence_thresh
        )

        print(f"\nProcessing complete!")
        print(f"Concatenated file: {concatenated_file}")
        print(f"Number of chunks created: {len(chunk_files)}")
        print(f"Chunks saved in: {args.chunks_folder}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # If running without command line arguments, use interactive mode
    import sys

    if len(sys.argv) == 1:
        print("Audio Concatenator and Silence Splitter")
        print("=" * 40)

        input_folder = input("Enter folder path containing WAV files: ").strip()
        if not os.path.isdir(input_folder):
            print(f"Error: Folder '{input_folder}' not found.")
            sys.exit(1)

        output_file = input(
            "Enter output filename (default: concatenated.wav): "
        ).strip()
        if not output_file:
            output_file = "concatenated.wav"

        chunks_folder = input("Enter chunks folder name (default: chunks): ").strip()
        if not chunks_folder:
            chunks_folder = "chunks"

        try:
            min_silence = int(
                input("Minimum silence length in milliseconds (default: 1000): ")
                or "1000"
            )
            silence_thresh = int(
                input("Silence threshold in dBFS (default: -40): ") or "-40"
            )
        except ValueError:
            print("Using default values...")
            min_silence = 1000
            silence_thresh = -40

        # Set up arguments for processing
        sys.argv = [
            sys.argv[0],
            "--input_folder",
            input_folder,
            "--output",
            output_file,
            "--chunks-folder",
            chunks_folder,
            "--min-silence",
            str(min_silence),
            "--silence-thresh",
            str(silence_thresh),
        ]

    main()
