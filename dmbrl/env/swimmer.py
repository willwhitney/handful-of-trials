from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

import numpy as np
from gym import utils
from gym.envs.mujoco import mujoco_env
import gym.envs.mujoco

class VisibleSwimmerEnv(gym.envs.mujoco.SwimmerEnv):
    def __init__(self):
        super().__init__()
        self.prev_qpos = None


    def _get_obs(self):
        if self.prev_qpos is not None:
            xvel = (self.sim.data.qpos.flat[:1] - self.prev_qpos[:1]) / self.dt
        else:
            xvel = np.zeros(1)
        return np.concatenate([
            xvel,
            self.sim.data.qpos.flat[1:],
            self.sim.data.qvel.flat,
        ])

    def step(self, action):
        self.prev_qpos = np.copy(self.sim.data.qpos.flat)
        return super().step(action)


    def reset_model(self):
        super().reset_model()
        self.prev_qpos = np.copy(self.sim.data.qpos.flat)
        return self._get_obs()
