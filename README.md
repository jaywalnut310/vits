# VITS 原神语音合成

本repo包含了我用于训练原神VITS模型对源代码做出的修改，以及新的config文件。

由于各种原因，模型和数据集暂无法公布，感兴趣可以自行提取，自行训练。

此外，也可以尝试使用公开的api：http://233366.proxy.nscc-gz.cn:8888/ 来进行尝试，请注意此模型禁止用于任何商业用途。请注意多次生成的效果不会一致，可以多次尝试来选择一次较好的效果。

支持的说话者：
['派蒙', '凯亚', '安柏', '丽莎', '琴', '香菱', '枫原万叶',
           '迪卢克', '温迪', '可莉', '早柚', '托马', '芭芭拉', '优菈',
           '云堇', '钟离', '魈', '凝光', '雷电将军', '北斗',
           '甘雨', '七七', '刻晴', '神里绫华', '戴因斯雷布', '雷泽',
           '神里绫人', '罗莎莉亚', '阿贝多', '八重神子', '宵宫',
           '荒泷一斗', '九条裟罗', '夜兰', '珊瑚宫心海', '五郎',
           '散兵', '女士', '达达利亚', '莫娜', '班尼特', '申鹤',
           '行秋', '烟绯', '久岐忍', '辛焱', '砂糖', '胡桃', '重云',
           '菲谢尔', '诺艾尔', '迪奥娜', '鹿野院平藏']

Query String 参数：

| 参数 | 类型 | 值 |
| ------------- | ------------- | ------------  |
| text | 字符串 |  生成的文本，支持常见标点符号。英文可能无法正常生成，数字请转换为对应的汉字再进行生成。 |
| speaker | 字符串 |  说话者名称。必须是上面的名称之一。 |
| noise | 浮点数 |  生成时使用的 noise_factor，可用于控制感情等变化程度。默认为0.667。 |
| noisew | 浮点数 |  生成时使用的 noise_factor_w，可用于控制音素发音长度变化程度。默认为0.8。 |
| length | 浮点数 |  生成时使用的 length_factor，可用于控制整体语速。默认为1.2。 |
| format | 字符串 |  生成语音的格式，必须为mp3或者wav。默认为mp3。 |

示例：http://233366.proxy.nscc-gz.cn:8888/?text=你好&speaker=派蒙




# VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech

### Jaehyeon Kim, Jungil Kong, and Juhee Son

In our recent [paper](https://arxiv.org/abs/2106.06103), we propose VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech.

Several recent end-to-end text-to-speech (TTS) models enabling single-stage training and parallel sampling have been proposed, but their sample quality does not match that of two-stage TTS systems. In this work, we present a parallel end-to-end TTS method that generates more natural sounding audio than current two-stage models. Our method adopts variational inference augmented with normalizing flows and an adversarial training process, which improves the expressive power of generative modeling. We also propose a stochastic duration predictor to synthesize speech with diverse rhythms from input text. With the uncertainty modeling over latent variables and the stochastic duration predictor, our method expresses the natural one-to-many relationship in which a text input can be spoken in multiple ways with different pitches and rhythms. A subjective human evaluation (mean opinion score, or MOS) on the LJ Speech, a single speaker dataset, shows that our method outperforms the best publicly available TTS systems and achieves a MOS comparable to ground truth.

Visit our [demo](https://jaywalnut310.github.io/vits-demo/index.html) for audio samples.

We also provide the [pretrained models](https://drive.google.com/drive/folders/1ksarh-cJf3F5eKJjLVWY0X1j1qsQqiS2?usp=sharing).

** Update note: Thanks to [Rishikesh (ऋषिकेश)](https://github.com/jaywalnut310/vits/issues/1), our interactive TTS demo is now available on [Colab Notebook](https://colab.research.google.com/drive/1CO61pZizDj7en71NQG_aqqKdGaA_SaBf?usp=sharing).

<table style="width:100%">
  <tr>
    <th>VITS at training</th>
    <th>VITS at inference</th>
  </tr>
  <tr>
    <td><img src="resources/fig_1a.png" alt="VITS at training" height="400"></td>
    <td><img src="resources/fig_1b.png" alt="VITS at inference" height="400"></td>
  </tr>
</table>


## Pre-requisites
0. Python >= 3.6
0. Clone this repository
0. Install python requirements. Please refer [requirements.txt](requirements.txt)
    1. You may need to install espeak first: `apt-get install espeak`
0. Download datasets
    1. Download and extract the LJ Speech dataset, then rename or create a link to the dataset folder: `ln -s /path/to/LJSpeech-1.1/wavs DUMMY1`
    1. For mult-speaker setting, download and extract the VCTK dataset, and downsample wav files to 22050 Hz. Then rename or create a link to the dataset folder: `ln -s /path/to/VCTK-Corpus/downsampled_wavs DUMMY2`
0. Build Monotonic Alignment Search and run preprocessing if you use your own datasets.
```sh
# Cython-version Monotonoic Alignment Search
cd monotonic_align
python setup.py build_ext --inplace

# Preprocessing (g2p) for your own datasets. Preprocessed phonemes for LJ Speech and VCTK have been already provided.
# python preprocess.py --text_index 1 --filelists filelists/ljs_audio_text_train_filelist.txt filelists/ljs_audio_text_val_filelist.txt filelists/ljs_audio_text_test_filelist.txt 
# python preprocess.py --text_index 2 --filelists filelists/vctk_audio_sid_text_train_filelist.txt filelists/vctk_audio_sid_text_val_filelist.txt filelists/vctk_audio_sid_text_test_filelist.txt
```


## Training Exmaple
```sh
# LJ Speech
python train.py -c configs/ljs_base.json -m ljs_base

# VCTK
python train_ms.py -c configs/vctk_base.json -m vctk_base
```


## Inference Example
See [inference.ipynb](inference.ipynb)
