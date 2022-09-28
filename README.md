# VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech

### Jaehyeon Kim, Jungil Kong, and Juhee Son

[Original paper](https://arxiv.org/abs/2106.06103). Several recent end-to-end text-to-speech (TTS) models enabling
single-stage training and parallel sampling have been
proposed, but their sample quality does not match that of two-stage TTS systems. In this work, we present a parallel
end-to-end TTS method that generates more natural sounding audio than current two-stage models. Our method adopts
variational inference augmented with normalizing flows and an adversarial training process, which improves the
expressive power of generative modeling. We also propose a stochastic duration predictor to synthesize speech with
diverse rhythms from input text. With the uncertainty modeling over latent variables and the stochastic duration
predictor, our method expresses the natural one-to-many relationship in which a text input can be spoken in multiple
ways with different pitches and rhythms. A subjective human evaluation (mean opinion score, or MOS) on the LJ Speech, a
single speaker dataset, shows that our method outperforms the best publicly available TTS systems and achieves a MOS
comparable to ground truth.

Author's [demo](https://jaywalnut310.github.io/vits-demo/index.html) audio samples.
Author's [pretrained models](https://drive.google.com/drive/folders/1ksarh-cJf3F5eKJjLVWY0X1j1qsQqiS2?usp=sharing).

<table style="width:100%">
  <tr>
    <th>VITS at training</th>
    <th>VITS at inference</th>
  </tr>
  <tr>
    <td><img src="files/resources/fig_1a.png" alt="VITS at training" height="400"></td>
    <td><img src="files/resources/fig_1b.png" alt="VITS at inference" height="400"></td>
  </tr>
</table>

## Setup environment

```commandline
sudo apt install libsndfile1 espeak gcc g++
conda env create -f env.yml

conda activate vits
cd monotonic_align
mkdir monotonic_align
python setup.py build_ext --inplace
```

for RTX 3090 TI
```commandline
sudo apt install libsndfile1 espeak gcc g++
conda create -n vits python=3.7
conda activate vits

pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111 torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
pip install tensorboard==2.3.0 scipy==1.7.3 librosa==0.9.1 phonemizer==3.0.1 unidecode==1.3.2 cython==0.29.27 matplotlib==3.5.1 tqdm==4.64.0 ipython==7.34.0 pydub==0.25.1 protobuf==3.20.1 numpy==1.21.6

cd monotonic_align
mkdir monotonic_align
python setup.py build_ext --inplace
```

Preprocessing (g2p) for your own datasets. Preprocessed phonemes for LJ Speech and VCTK have been already provided.

```commandline
python preprocess.py --text_index 1 --filelists files/filelists/ljs_audio_text_train_filelist.txt files/filelists/ljs_audio_text_val_filelist.txt files/filelists/ljs_audio_text_test_filelist.txt 
python preprocess.py --text_index 2 --filelists files/filelists/vctk_audio_sid_text_train_filelist.txt files/filelists/vctk_audio_sid_text_val_filelist.txt files/filelists/vctk_audio_sid_text_test_filelist.txt
```

## Training Exmaple

```sh
# LJ Speech
python train.py -c configs/ljs_base_cleaned_44khz.json -m ljs_base

# VCTK
python train_ms.py -c configs/vctk_base.json -m vctk_base
```

## Inference Example

See [inference.ipynb](tools/jnotebooks/synthesis/inference.ipynb)
