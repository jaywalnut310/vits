import argparse
import json
import os

from src.model.checkpoint import latest_checkpoint_path


class HParams:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if type(v) == dict:
                v = HParams(**v)
            self[k] = v

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()


def get_hparams(init=True):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default="./configs/base.json",
                        help='JSON file for configuration')
    parser.add_argument('--model-dir', type=str, required=False)
    parser.add_argument('--checkpoint-d', type=str, required=False)
    parser.add_argument('--checkpoint-g', type=str, required=False)
    parser.add_argument('-m', '--model', type=str, required=True,
                        help='Model name')
    args = parser.parse_args()

    model_dir = os.path.join("./logs", args.model) if not args.model_dir else os.path.join(args.model_dir, args.model)

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    checkpoint_d = latest_checkpoint_path(model_dir, "D_*.pth") if not args.checkpoint_d else os.path.join(model_dir,
                                                                                                           args.checkpoint_d)
    checkpoint_g = latest_checkpoint_path(model_dir, "G_*.pth") if not args.checkpoint_d else os.path.join(model_dir,
                                                                                                           args.checkpoint_g)

    config_path = args.config
    config_save_path = os.path.join(model_dir, "config.json")
    if init:
        with open(config_path, "r") as f:
            data = f.read()
        with open(config_save_path, "w") as f:
            f.write(data)
    else:
        with open(config_save_path, "r") as f:
            data = f.read()
    config = json.loads(data)

    hparams = HParams(**config)
    hparams.model_dir = model_dir
    hparams.checkpoint_d = checkpoint_d
    hparams.checkpoint_g = checkpoint_g
    return hparams


def get_hparams_from_file(config_path):
    with open(config_path, "r") as f:
        data = f.read()
    config = json.loads(data)

    hparams = HParams(**config)
    return hparams
