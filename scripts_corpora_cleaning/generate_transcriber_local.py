import os
import whisper

# Path to the folder with .wav files
INPUT_FOLDER = "chunks/"
OUTPUT_FILE = "transcriptions.csv"

# Load Whisper model
model = whisper.load_model("base")  # you can use "tiny", "base", "small", "medium", "large"

# Open the output file in append mode
with open(OUTPUT_FILE, "a", encoding="utf-8") as out_file:
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(".wav"):
            file_path = os.path.join(INPUT_FOLDER, filename)
            print(f"Transcribing {filename}...")

            # Transcribe the audio
            result = model.transcribe(file_path)
            transcription = result["text"].strip()

            # Write to output file in the format: file_name (no extension)|transcription
            file_stem = os.path.splitext(filename)[0]
            out_file.write(f"{file_stem}|{transcription}\n")
            print(f"Saved transcription for {filename}.")

