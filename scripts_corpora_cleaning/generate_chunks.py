import asyncio
from openai import AsyncOpenAI
import time


async def generate_chunks():
    start_time = time.time()
    semaphore = asyncio.Semaphore(30)  # Limit concurrency (tune as needed)
    tasks = []
    batch_size = 500
    # read wavlist line by line
    with open("wavlist.txt", "r") as f:
        wavlist = [line.strip() for line in f]

    async def process_file(file):
        async with semaphore:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-i",
                file,
                "-ar",
                "22050",  # Set sample rate to 22050 Hz
                "-ac",
                "1",  # Set to mono
                "-sample_fmt",
                "s16",  # Set to 16-bit PCM
                f"../data/chunks/{wavlist.index(file)}.wav",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()

    for i in range(0, len(wavlist), batch_size):
        batch = wavlist[i : i + batch_size]
        tasks = [process_file(file) for file in batch]
        await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    print(f"Walltime: {elapsed:.2f} seconds")


asyncio.run(generate_chunks())
