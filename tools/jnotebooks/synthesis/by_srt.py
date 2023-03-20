import os
import re
from pathlib import Path

import pyperclip
from scipy.io.wavfile import write

from src.core import SrtPair
from src.logger import get_logger
from src.model.config import Speaker, get_inference_configs
from src.text.symbols import get_vocabulary

logger = get_logger(__name__)

vocabulary, _, _ = get_vocabulary('lt')


def __approve_input_text(entry_text: str):
    i_option = input(f"Edit entry text? Note that the symbol `*` is removed when synthesizing.\n"
                     f"{entry_text}\n"
                     f"[Y/n]: ")
    if i_option.lower() != 'y':
        return entry_text

    while True:
        in_text = input("Enter text:\n")
        oov_symbols = set(re.findall(fr"[^{''.join(vocabulary).replace('-', '')}]", in_text))

        if '-' in oov_symbols:
            oov_symbols.remove('-')
        if '*' in oov_symbols:
            oov_symbols.remove('*')

        if not oov_symbols or all([s == '-' for s in oov_symbols]):
            return in_text
        print(f"OOV symbols `{oov_symbols}` in input text `{in_text}`")


if __name__ == '__main__':
    speaker = Speaker.AURIMAS_ALTORIU_SESELY_22
    speed_multiplier = 0.9  # 1.0 - full speed; lower - faster
    device = 'gpu'
    cuda_device = 1

    config = get_inference_configs(speakers=[speaker], speed_multiplier=speed_multiplier,
                                   device=device, cuda_device=cuda_device)[speaker]

    audiobook_dirname = "greetings-new_2023-17-02_13-23-45"
    audiobook_dir = Path("/home/arnas/inovoice/repos/vits/files/audio/audiobooks") / speaker.value / str(
        config.checkpoint_step) / audiobook_dirname

    chapter_idx = 0
    book_name = "greetings"
    filename = f'{speaker.value}_{config.checkpoint_step}_{chapter_idx}-{book_name}'

    srt_path = audiobook_dir / f"{filename}.srt"
    wav_path = audiobook_dir / f"{filename}.wav"
    output_dir = audiobook_dir / "out"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filter_marked = False

    srt: SrtPair = SrtPair.from_filepaths_pair(srt_path, wav_path)
    tmp_filepath = '/home/aai-labs/tmp_audio.wav'  # used as a temporary file to be able to play audio
    for idx, entry in enumerate(srt.entries):
        if filter_marked and '*' not in entry.text:
            continue

        print(f"Synthesizing `{entry.text}`")
        entry.audio.export(tmp_filepath, format='wav')
        while True:
            os.system(f"ffplay {tmp_filepath}")

            try:
                option = int(input("[1] Next entry\n[2] Resynthesize\n[3] Save\n[OTHER] Replay audio\n"))
            except:
                print("WRONG INPUT...")
                continue

            if option == 1:
                print("Moving to the next entry...")
                break
            elif option == 2:
                curr_entry = srt.entries[idx]
                print(f"Resynthesizing... {curr_entry.text}")
                print(f"The text is copied to clipboard.")
                # If PyQt4 module not found error is thrown, run `sudo apt-get install xclip xsel
                pyperclip.copy(curr_entry.text)
                text = __approve_input_text(curr_entry.text)

                try:
                    utterance = config.synthesizer.synthesize(text.replace('*', '').strip())
                    write(tmp_filepath, config.synthesizer.sample_rate, utterance.audio)

                    srt.update_entry_by_utternace(idx, utterance)
                except Exception as e:
                    print(f"Error: {e}")
                    continue

            elif option == 3:
                srt.save_pair(output_dir)

    srt.save_pair(output_dir)
    os.remove(tmp_filepath)
    print("SRT fixing complete!")
