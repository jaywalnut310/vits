import glob
import os

import torch

from src.logger import get_logger

logger = get_logger(__name__)


def load_checkpoint_for_inference(checkpoint_path, model):
    assert os.path.isfile(checkpoint_path)
    logger.info(f"Loading checkpoint at {checkpoint_path}")
    checkpoint_dict = torch.load(checkpoint_path, map_location='cpu')

    saved_state_dict = checkpoint_dict['model']
    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()

    new_state_dict = {}
    for k, v in state_dict.items():
        try:
            new_state_dict[k] = saved_state_dict[k]
        except:
            logger.info("no `warm_start` or `ignore_layers` hyperparameter found or %s is not in the checkpoint" % k)
            new_state_dict[k] = v

    if hasattr(model, 'module'):
        model.module.load_state_dict(new_state_dict, strict=False)
    else:
        model.load_state_dict(new_state_dict, strict=False)

    logger.info("Loaded checkpoint '{}'".format(checkpoint_path))
    return model


def load_checkpoint(hps_train, checkpoint_path, model, optimizer=None):
    assert os.path.isfile(checkpoint_path)
    logger.info(f"Loading checkpoint at {checkpoint_path}")
    checkpoint_dict = torch.load(checkpoint_path, map_location='cpu')
    iteration = checkpoint_dict['iteration']
    learning_rate = checkpoint_dict['learning_rate']

    optimizer = __load_optimizer(optimizer, checkpoint_dict, hps_train)
    model = __load_state_dict(model, checkpoint_dict, hps_train)

    logger.info(f"Loaded checkpoint '{checkpoint_path}' (iteration {iteration})")
    return model, optimizer, learning_rate, iteration


def __load_optimizer(optimizer, checkpoint_dict, hps_train):
    if optimizer is not None:
        if hps_train.warm_start:
            ignored_layer_ids = [idx for idx, layer_name in enumerate(checkpoint_dict['model']) if
                                 layer_name in hps_train.ignore_layers]
            opt_state = checkpoint_dict['optimizer']['state']
            saved_optimizer_state = {k: v for idx, (k, v) in enumerate(opt_state.items()) if
                                     idx not in ignored_layer_ids}
            checkpoint_dict['optimizer']['state'] = saved_optimizer_state
            optimizer.load_state_dict(checkpoint_dict['optimizer'])
        else:
            optimizer.load_state_dict(checkpoint_dict['optimizer'])
    return optimizer


def __load_state_dict(model, checkpoint_dict, hps_train):
    saved_state_dict = checkpoint_dict['model']
    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()

    new_state_dict = {}
    for k, v in state_dict.items():
        try:
            if not hps_train.warm_start:
                new_state_dict[k] = saved_state_dict[k]
            elif hps_train.warm_start and k not in hps_train.ignore_layers:
                new_state_dict[k] = saved_state_dict[k]
        except:
            logger.info("no `warm_start` or `ignore_layers` hyperparameter found or %s is not in the checkpoint" % k)
            new_state_dict[k] = v

    if hasattr(model, 'module'):
        model.module.load_state_dict(new_state_dict, strict=False)
    else:
        model.load_state_dict(new_state_dict, strict=False)
    return model


def save_checkpoint(model, optimizer, learning_rate, iteration, checkpoint_path):
    logger.info(f"Saving model and optimizer state at iteration {iteration} to {checkpoint_path}")

    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    torch.save({'model': state_dict,
                'iteration': iteration,
                'optimizer': optimizer.state_dict(),
                'learning_rate': learning_rate}, checkpoint_path)  # TODO: save vocabulary

    logger.info(f"Model saved to {checkpoint_path}")


def latest_checkpoint_path(dir_path, regex="G_*.pth"):
    f_list = glob.glob(os.path.join(dir_path, regex))
    f_list.sort(key=lambda f: int("".join(filter(str.isdigit, f))))
    if not f_list:
        return None

    x = f_list[-1]
    print(x)
    return x
