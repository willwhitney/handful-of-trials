from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import tensorflow as tf
from dotmap import DotMap
import gym
import os
import uuid

from dmbrl.misc.DotmapUtils import get_required_argument
from dmbrl.modeling.layers import FC
import dmbrl.env

from baselines import bench

monitor_root = '/private/home/willwhitney/code/handful-of-trials/monitor-logs'

class SwimmerConfigModule:
    ENV_NAME = "VisibleSwimmer-v2"
    TASK_HORIZON = 1000
    NTRAIN_ITERS = 100000
    NROLLOUTS_PER_ITER = 1
    PLAN_HOR = 100
    MODEL_IN, MODEL_OUT = 12, 10
    GP_NINDUCING_POINTS = 300

    def __init__(self):
        experiment_name = "paper-xvel2_taskhorizon{}_trainiters{}_rolloutsperiter{}_planhor_{}".format(
                self.TASK_HORIZON, self.NTRAIN_ITERS, self.NROLLOUTS_PER_ITER, self.PLAN_HOR)
        experiment_name += '_seed' + str(uuid.uuid4())[:8]

        self.ENV = gym.make(self.ENV_NAME)

        monitor_dir = os.path.join(monitor_root, self.ENV_NAME, experiment_name)
        os.makedirs(monitor_dir, exist_ok=True)
        self.ENV = bench.Monitor(
                self.ENV, 
                os.path.join(monitor_dir, '0'),
                allow_early_resets=True)

        cfg = tf.ConfigProto()
        cfg.gpu_options.allow_growth = True
        self.SESS = tf.Session(config=cfg)
        self.NN_TRAIN_CFG = {"epochs": 5}
        self.OPT_CFG = {
            "Random": {
                "popsize": 2500
            },
            "CEM": {
                "popsize": 500,
                "num_elites": 50,
                "max_iters": 5,
                "alpha": 0.1
            }
        }

    # @staticmethod
    # def obs_preproc(obs):
    #     if isinstance(obs, np.ndarray):
    #         return np.concatenate([obs[:, 1:2], np.sin(obs[:, 2:3]), np.cos(obs[:, 2:3]), obs[:, 3:]], axis=1)
    #     else:
    #         return tf.concat([obs[:, 1:2], tf.sin(obs[:, 2:3]), tf.cos(obs[:, 2:3]), obs[:, 3:]], axis=1)

    # @staticmethod
    # def obs_postproc(obs, pred):
    #     if isinstance(obs, np.ndarray):
    #         return np.concatenate([pred[:, :1], obs[:, 1:] + pred[:, 1:]], axis=1)
    #     else:
    #         return tf.concat([pred[:, :1], obs[:, 1:] + pred[:, 1:]], axis=1)

    # @staticmethod
    # def targ_proc(obs, next_obs):
    #     return np.concatenate([next_obs[:, :1], next_obs[:, 1:] - obs[:, 1:]], axis=1)

    @staticmethod
    def obs_cost_fn(obs):
        return -obs[:, 0]

    @staticmethod
    def ac_cost_fn(acs):
        if isinstance(acs, np.ndarray):
            return 0.0 * np.sum(np.square(acs), axis=1)
        else:
            return 0.0 * tf.reduce_sum(tf.square(acs), axis=1)

    def nn_constructor(self, model_init_cfg):
        model = get_required_argument(model_init_cfg, "model_class", "Must provide model class")(DotMap(
            name="model", num_networks=get_required_argument(model_init_cfg, "num_nets", "Must provide ensemble size"),
            sess=self.SESS, load_model=model_init_cfg.get("load_model", False),
            model_dir=model_init_cfg.get("model_dir", None)
        ))
        if not model_init_cfg.get("load_model", False):
            model.add(FC(200, input_dim=self.MODEL_IN, activation="swish", weight_decay=0.000025))
            model.add(FC(200, activation="swish", weight_decay=0.00005))
            model.add(FC(200, activation="swish", weight_decay=0.000075))
            model.add(FC(200, activation="swish", weight_decay=0.000075))
            model.add(FC(self.MODEL_OUT, weight_decay=0.0001))
        model.finalize(tf.train.AdamOptimizer, {"learning_rate": 0.001})
        return model

    def gp_constructor(self, model_init_cfg):
        model = get_required_argument(model_init_cfg, "model_class", "Must provide model class")(DotMap(
            name="model",
            kernel_class=get_required_argument(model_init_cfg, "kernel_class", "Must provide kernel class"),
            kernel_args=model_init_cfg.get("kernel_args", {}),
            num_inducing_points=get_required_argument(
                model_init_cfg, "num_inducing_points", "Must provide number of inducing points."
            ),
            sess=self.SESS
        ))
        return model


CONFIG_MODULE = SwimmerConfigModule
