import os
from pathlib import Path

from scipy.io.wavfile import write

from hparams import get_hparams_from_file
from src.core import SrtPair
from src.logger import get_logger
from src.model.synthesizer import InferenceConfig

logger = get_logger(__name__)


def __approve_input_text(entry_text: str):
    i_option = input(f"Edit entry text? Note that the symbol `*` is removed when synthesizing.\n"
                         f"{entry_text}\n"
                         f"[Y/n]: ")

    return entry_text if i_option.lower() != 'y' else input("Enter text:\n")


if __name__ == '__main__':
    checkpoint_step = 250000
    speaker = 'giedrius_studio_44'
    device = 1

    synthesizer = InferenceConfig(
        checkpoint_step=checkpoint_step,
        config_name='giedrius_studio_44khz',
        speaker='giedrius_studio_44',
        stressed=True,
        device=device,
    ).synthesizer

    filename = f'kur_vasara_amzina_{speaker}_{checkpoint_step}'
    base_dir = "/home/aai-labs/inovoice/repos/vits/files/audio/audiobooks"
    srt_path = Path(f"{base_dir}/{speaker}/{checkpoint_step}/{filename}.srt")
    wav_path = Path(f"{base_dir}/{speaker}/{checkpoint_step}/{filename}.wav")
    output_dir = Path(f"{base_dir}/{speaker}/{checkpoint_step}/out")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filter_marked = False

    srt: SrtPair = SrtPair.from_filepaths_pair(srt_path, wav_path)
    tmp_filepath = '/home/aai-labs/tmp_audio.wav'  # used as a temporary file to be able to play audio
    for idx, entry in enumerate(srt.entries):
        if filter_marked and '*' not in entry.text:
            continue

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
                text = __approve_input_text(curr_entry.text)

                utterance = synthesizer.synthesize(text.replace('*', '').strip())
                write(tmp_filepath, synthesizer.sample_rate, utterance.audio)

                srt.update_entry_by_utternace(idx, utterance)
            elif option == 3:
                srt.save_pair(output_dir)

    srt.save_pair(output_dir)
    os.remove(tmp_filepath)
    print("SRT fixing complete!")
