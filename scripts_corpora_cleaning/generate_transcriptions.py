import asyncio
import glob
import io
import json
import os
from pathlib import Path
from openai import AsyncOpenAI
import time
from datasets import Dataset, Audio
import soundfile as sf


def load_dataset_local(path):
    path = Path(os.path.join(path))
    wav_files = list(path.rglob("*.wav"))
    dataset_dict = dict({"audio": [], "sentence": []})
    for file in wav_files:
        transcription_path = str(file).replace(".wav", ".txt")
        if not (Path(transcription_path).exists()):
            sentence = ""
        else:
            continue
        dataset_dict["audio"].append(str(file.resolve()))
        dataset_dict["sentence"].append(sentence)
    return Dataset.from_dict(dataset_dict).cast_column("audio", Audio())


async def generate_chunks():
    start_time = time.time()
    semaphore = asyncio.Semaphore(60)  # Limit concurrency (tune as needed)
    batch_size = 20  # number of jobs to run in parallel
    dataset = load_dataset_local(
        "/mnt/seagate8tbhdd/corpora/TTS-Portuguese-Corpus/downsampled_wavs/"
    )

    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))  # for whisper

    clients = []
    clients.append(AsyncOpenAI(api_key="EMPTY", base_url="http://5090.local:8000/v1"))
    clients.append(AsyncOpenAI(api_key="EMPTY", base_url="http://5090.local:8001/v1"))

    async def process_file(entry, client_index):
        async with semaphore:
            try:
                audio_array = entry["array"]
                sample_rate = entry["sampling_rate"]
                path = entry.metadata.path
                with io.BytesIO() as buffer:
                    sf.write(buffer, audio_array, sample_rate, format="WAV")
                    buffer.seek(0)
                    resp = await clients[client_index].audio.transcriptions.create(
                        file=buffer,
                        model="openai/whisper-large-v3",
                        language="pt",
                        temperature=0.0,
                        response_format="text",
                    )
                    transcription = json.loads(resp)["text"]
                    # Save transcription to file
                    transcription_path = path.replace(".wav", ".txt")
                    with open(transcription_path, "w") as f:
                        f.write(transcription.strip())
            except Exception as e:
                print(f"Error processing {entry.metadata.path}: {e}")
                # log to file
                with open("error_log.txt", "a") as f:
                    f.write(f"Error processing {entry.metadata.path}: {e}\n")
                    f.write("===========================================")
                return

    for i in range(0, len(dataset), batch_size):
        batch_1 = dataset[i : int(i + (batch_size / 2))]
        batch_2 = dataset[int(i + batch_size / 2) : i + batch_size]
        tasks = []

        for entry1, entry2 in zip(batch_1["audio"], batch_2["audio"]):
            tasks.append(process_file(entry1, 0))
            tasks.append(process_file(entry2, 1))

        # If odd number, add all sequentially
        if len(batch_1["audio"]) != len(batch_2["audio"]):
            for entry in batch_1["audio"]:
                tasks.append(process_file(entry, 0))
            for entry in batch_2["audio"]:
                tasks.append(process_file(entry, 1))

        await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    print(f"Walltime: {elapsed:.2f} seconds")


asyncio.run(generate_chunks())
