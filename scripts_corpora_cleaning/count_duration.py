import os
from pydub import AudioSegment

# Change this to your directory path
directory = "/media/4tbdrive/engines/vits/allison_corpora/data/chunks/"

total_duration = 0.0

for filename in os.listdir(directory):
    if filename.lower().endswith(".wav"):
        filepath = os.path.join(directory, filename)
        try:
            audio = AudioSegment.from_wav(filepath)
            duration_seconds = len(audio) / 1000.0  # pydub returns milliseconds
            total_duration += duration_seconds
            print(f"{directory}/{filename} {duration_seconds:.2f} seconds")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Convert to hh:mm:ss
hours = int(total_duration // 3600)
minutes = int((total_duration % 3600) // 60)
seconds = int(total_duration % 60)

print("\nTotal duration:")
print(f"{total_duration:.2f} seconds")
print(f"{hours:02}:{minutes:02}:{seconds:02} (hh:mm:ss)")
