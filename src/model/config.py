from enum import Enum
from pathlib import Path
from typing import List

from hparams import get_hparams_from_file
from src.model.synthesizer import Synthesizer


class Speaker(Enum):
    GIEDRIUS_BASE_44 = "giedrius_arbaciauskas_base_44"
    AURIMAS_AUDIOBOOK_44 = "aurimas_nausedas_44"
    AURIMAS_AUDIOBOOK_22 = "aurimas_nausedas_22"
    AURIMAS_ALTORIU_SESELY_22 = "aurimas_altoriu_sesely_22"
    AURIMAS_ALTORIU_SESELY_44 = "aurimas_altoriu_sesely_44"
    GIEDRIUS_STUDIO_44 = "giedrius_studio_44_ft_base_mel160"
    MILDA_STUDIO_44 = "milda_no_noise_44_ft_base_mel160"
    MILDA_STUDIO_22 = "milda_no_noise_22"
    MILDA_TEKA_UPE_PRO_SALI_44 = "milda_teka_upe_pro_sali_44"
    MILDA_TEKA_UPE_PRO_SALI_22 = "milda_teka_upe_pro_sali_22"
    MILDA_TEKA_UPE_PRO_SALI_QUESTIONS_22 = "milda_teka_upe_pro_sali_questions_22"
    CHILD_VOICE_GERDA = "child_voice_gerda"
    CHILD_VOICE_LUKAS = "child_voice_lukas"
    CHILD_VOICE_TIMAS = "child_voice_timas"
    AMATEUR_44 = "arnas_44_ft_giedrius_base"
    LJS_BASE_44 = "ljs_base_44khz"
    OPENSLR_FEMALE_44 = "openslr_92_44"
    OPENSLR_MALE_44 = "openslr_9017_44"
    OPENSLR_MALE_13130_44 = "openslr_9017_13130_44"


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

    def __init__(self, config_name: str, checkpoint_step: int, speaker: Speaker,
                 clean_accentuation: bool = False, speed_multiplier: float = 1.0,
                 audiobook_synthesis: bool = False, device: str = 'gpu', cuda_device: int = 0):

        self.config_name = config_name
        self.speaker = speaker
        self.clean_accentuation = clean_accentuation
        self.speed_multiplier = speed_multiplier

        self.checkpoint_step = checkpoint_step
        self.checkpoint_path = self._model_base_dir / f"{speaker.value}/G_{checkpoint_step}.pth"

        if audiobook_synthesis:
            self.output_dir = self._output_base_dir / f"audiobooks/{speaker.value}/{checkpoint_step}"
        else:
            self.output_dir = self._output_base_dir / f"samples/{speaker.value}/{checkpoint_step}"

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        hps = get_hparams_from_file(self._configs_base_dir / f"{config_name}.json")
        self.synthesizer = Synthesizer(hps, self.checkpoint_path, model_name=f"{speaker.value}_{checkpoint_step}",
                                       clean_accentuation=clean_accentuation, speed_multiplier=speed_multiplier,
                                       device=device, cuda_device=cuda_device)


def get_inference_configs(speakers: List[Speaker], audiobook_synthesis: bool = False, speed_multiplier: float = 1.0,
                          device: str = 'gpu', cuda_device: int = 0):
    configs = {}
    for speaker in speakers:
        if speaker == Speaker.GIEDRIUS_BASE_44:
            configs[Speaker.GIEDRIUS_BASE_44] = InferenceConfig(
                checkpoint_step=2175000,
                config_name='giedrius_44khz',
                speaker=Speaker.GIEDRIUS_BASE_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device
            )

        if speaker == Speaker.AURIMAS_AUDIOBOOK_22:
            configs[Speaker.AURIMAS_AUDIOBOOK_22] = InferenceConfig(
                checkpoint_step=225000,
                config_name='aurimas_22khz',
                speaker=Speaker.AURIMAS_AUDIOBOOK_22,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.AURIMAS_AUDIOBOOK_44:
            configs[Speaker.AURIMAS_AUDIOBOOK_44] = InferenceConfig(
                checkpoint_step=380000,
                config_name='aurimas_44khz',
                speaker=Speaker.AURIMAS_AUDIOBOOK_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.AURIMAS_ALTORIU_SESELY_22:
            configs[Speaker.AURIMAS_ALTORIU_SESELY_22] = InferenceConfig(
                checkpoint_step=180000,
                config_name='aurimas_altoriu_sesely_22khz',
                speaker=Speaker.AURIMAS_ALTORIU_SESELY_22,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.AURIMAS_ALTORIU_SESELY_44:
            configs[Speaker.AURIMAS_ALTORIU_SESELY_44] = InferenceConfig(
                checkpoint_step=120000,
                config_name='aurimas_altoriu_sesely_44khz',
                speaker=Speaker.AURIMAS_ALTORIU_SESELY_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.GIEDRIUS_STUDIO_44:
            configs[Speaker.GIEDRIUS_STUDIO_44] = InferenceConfig(
                checkpoint_step=272500,
                config_name='giedrius_studio_44khz',
                speaker=Speaker.GIEDRIUS_STUDIO_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.MILDA_STUDIO_44:
            configs[Speaker.MILDA_STUDIO_44] = InferenceConfig(
                # checkpoint_step=100000,
                checkpoint_step=185000,
                config_name='milda_no_noise_44khz',
                speaker=Speaker.MILDA_STUDIO_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.MILDA_STUDIO_22:
            configs[Speaker.MILDA_STUDIO_22] = InferenceConfig(
                checkpoint_step=68000,
                config_name='milda_22khz',
                speaker=Speaker.MILDA_STUDIO_22,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.MILDA_TEKA_UPE_PRO_SALI_22:
            configs[Speaker.MILDA_TEKA_UPE_PRO_SALI_22] = InferenceConfig(
                checkpoint_step=40000,
                config_name='milda_teka_upe_pro_sali_22khz',
                speaker=Speaker.MILDA_TEKA_UPE_PRO_SALI_22,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.MILDA_TEKA_UPE_PRO_SALI_QUESTIONS_22:
            configs[Speaker.MILDA_TEKA_UPE_PRO_SALI_QUESTIONS_22] = InferenceConfig(
                checkpoint_step=1500,
                config_name='milda_teka_upe_pro_sali_questions_22khz',
                speaker=Speaker.MILDA_TEKA_UPE_PRO_SALI_QUESTIONS_22,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.MILDA_TEKA_UPE_PRO_SALI_44:
            configs[Speaker.MILDA_TEKA_UPE_PRO_SALI_44] = InferenceConfig(
                # checkpoint_step=47500,
                checkpoint_step=62500,
                config_name='milda_teka_upe_pro_sali_44khz',
                speaker=Speaker.MILDA_TEKA_UPE_PRO_SALI_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.CHILD_VOICE_GERDA:
            configs[Speaker.CHILD_VOICE_GERDA] = InferenceConfig(
                checkpoint_step=60000,
                config_name='gerda_44khz',
                speaker=Speaker.CHILD_VOICE_GERDA,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.CHILD_VOICE_LUKAS:
            configs[Speaker.CHILD_VOICE_LUKAS] = InferenceConfig(
                checkpoint_step=12000,
                config_name='lukas_44khz',
                speaker=Speaker.CHILD_VOICE_LUKAS,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.CHILD_VOICE_TIMAS:
            configs[Speaker.CHILD_VOICE_TIMAS] = InferenceConfig(
                checkpoint_step=20000,
                config_name='timas_44khz',
                speaker=Speaker.CHILD_VOICE_TIMAS,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.AMATEUR_44:
            configs[Speaker.AMATEUR_44] = InferenceConfig(
                checkpoint_step=36000,
                config_name='arnas_44khz',
                speaker=Speaker.AMATEUR_44,
                clean_accentuation=False,
                speed_multiplier=speed_multiplier,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.LJS_BASE_44:
            configs[Speaker.LJS_BASE_44] = InferenceConfig(
                checkpoint_step=1320000,
                config_name='ljs_base_44khz',
                speaker=Speaker.LJS_BASE_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.OPENSLR_FEMALE_44:
            configs[Speaker.OPENSLR_FEMALE_44] = InferenceConfig(
                checkpoint_step=2230000,
                config_name='openslr_92_44khz',
                speaker=Speaker.OPENSLR_FEMALE_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.OPENSLR_MALE_44:
            configs[Speaker.OPENSLR_MALE_44] = InferenceConfig(
                checkpoint_step=3105000,
                config_name='openslr_9017_44khz',
                speaker=Speaker.OPENSLR_MALE_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

        if speaker == Speaker.OPENSLR_MALE_13130_44:
            configs[Speaker.OPENSLR_MALE_13130_44] = InferenceConfig(
                checkpoint_step=955000,
                config_name='openslr_9017_13130_44khz',
                speaker=Speaker.OPENSLR_MALE_13130_44,
                clean_accentuation=True,
                audiobook_synthesis=audiobook_synthesis,
                device=device, cuda_device=cuda_device,
            )

    if len(configs) != len(speakers):
        raise ValueError(f"Invalid speakers provided: {set(speakers).difference(set(configs.keys()))}")

    return configs
