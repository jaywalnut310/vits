from enum import Enum
from pathlib import Path
from typing import List

from hparams import get_hparams_from_file
from src.model.synthesizer import Synthesizer


class Speaker(Enum):
    GIEDRIUS_BASE_44 = "giedrius_arbaciauskas_base_44"
    AURIMAS_STUDIO_44 = "aurimas_nausedas_44"
    GIEDRIUS_STUDIO_44 = "giedrius_studio_44_ft_base_mel160"
    MILDA_STUDIO_44 = "milda_no_noise_44_ft_base_mel160"
    AMATEUR_44 = "arnas_44_ft_giedrius_base"
    LJS_BASE_44 = "ljs_base_44khz"
    OPENSLR_FEMALE_44 = "openslr_92_44"
    OPENSLR_MALE_44 = "openslr_9017_44"


class InferenceConfig:
    synthesizer: Synthesizer

    output_dir: Path = None
    checkpoint_step: int
    checkpoint_path: Path
    speaker: Speaker
    clean_accentuation: bool

    _model_base_dir = Path("/home/arnas/inovoice/models")
    _output_base_dir = Path("/home/arnas/inovoice/repos/vits/files/audio")
    _configs_base_dir = Path("/home/arnas/inovoice/repos/vits/files/configs")

    def __init__(self, config_name: str, checkpoint_step: int, speaker: Speaker, clean_accentuation: bool = False,
                 audiobook_synthesis: bool = False, device: str = 'gpu'):

        self.config_name = config_name
        self.speaker = speaker
        self.clean_accentuation = clean_accentuation

        self.checkpoint_step = checkpoint_step
        self.checkpoint_path = self._model_base_dir / f"{speaker.value}/G_{checkpoint_step}.pth"

        if audiobook_synthesis:
            self.output_dir = self._output_base_dir / f"audiobooks/{speaker.value}/{checkpoint_step}"
        else:
            self.output_dir = self._output_base_dir / f"samples/{speaker.value}/{checkpoint_step}"

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        hps = get_hparams_from_file(self._configs_base_dir / f"{config_name}.json")
        self.synthesizer = Synthesizer(hps, self.checkpoint_path, device=device)


def get_inference_configs(speakers: List[Speaker], audiobook_synthesis: bool = False, device: str = 'gpu'):
    configs = {}
    for speaker in speakers:
        if speaker == Speaker.GIEDRIUS_BASE_44:
            configs[Speaker.GIEDRIUS_BASE_44] = InferenceConfig(
                checkpoint_step=2175000,
                config_name='giedrius_44khz',
                speaker=Speaker.GIEDRIUS_BASE_44,
                clean_accentuation=False,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.AURIMAS_STUDIO_44:
            configs[Speaker.AURIMAS_STUDIO_44] = InferenceConfig(
                checkpoint_step=380000,
                config_name='aurimas_studio_44khz',
                speaker=Speaker.AURIMAS_STUDIO_44,
                clean_accentuation=False,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.GIEDRIUS_STUDIO_44:
            configs[Speaker.GIEDRIUS_STUDIO_44] = InferenceConfig(
                checkpoint_step=272500,
                config_name='giedrius_studio_44khz',
                speaker=Speaker.GIEDRIUS_STUDIO_44,
                clean_accentuation=False,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.MILDA_STUDIO_44:
            configs[Speaker.MILDA_STUDIO_44] = InferenceConfig(
                checkpoint_step=100000,
                # checkpoint_step=185000,
                config_name='milda_no_noise_44khz',
                speaker=Speaker.MILDA_STUDIO_44,
                clean_accentuation=False,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.AMATEUR_44:
            configs[Speaker.AMATEUR_44] = InferenceConfig(
                checkpoint_step=36000,
                config_name='arnas_44khz',
                speaker=Speaker.AMATEUR_44,
                clean_accentuation=False,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.LJS_BASE_44:
            configs[Speaker.LJS_BASE_44] = InferenceConfig(
                checkpoint_step=1320000,
                config_name='ljs_base_44khz',
                speaker=Speaker.LJS_BASE_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.OPENSLR_FEMALE_44:
            configs[Speaker.OPENSLR_FEMALE_44] = InferenceConfig(
                checkpoint_step=2230000,
                config_name='openslr_92_44khz',
                speaker=Speaker.OPENSLR_FEMALE_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

        if speaker == Speaker.OPENSLR_MALE_44:
            configs[Speaker.OPENSLR_MALE_44] = InferenceConfig(
                checkpoint_step=2740000,
                config_name='openslr_9017_44khz',
                speaker=Speaker.OPENSLR_MALE_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device,
            )

    if len(configs) != len(speakers):
        raise ValueError(f"Invalid speakers provided: {set(speakers).difference(set(configs.keys()))}")

    return configs
