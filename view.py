import os.path as osp
import os

import gym
import numpy as np
from matplotlib.animation import PillowWriter
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from baselines.ppo2 import ppo2
from baselines.common.models import build_impala_cnn
from baselines.common.vec_env import (
    VecMonitor,
    DummyVecEnv,
)

import Maze

LOG_DIR = './maze_train_folder'
#Goes much faster without gpu for some reason...
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

def env_fn():
    return gym.make('maze-v0', start_level=0, num_levels=50)
envs = [env_fn for x in range(64)]
venv = DummyVecEnv(envs)

config = tf.ConfigProto()
sess = tf.Session(config=config)
sess.__enter__()

conv_fn = lambda x: build_impala_cnn(x, depths=[16,32,32], emb_size=256)

final_model = ppo2.learn(
    env=venv,
    network=conv_fn,
    total_timesteps=0,
    mpi_rank_weight=0,
    update_fn=None,
    init_fn=None,
)

loadpath = osp.join(LOG_DIR, 'final')
final_model.load(loadpath)

obs = venv.reset()
fig = plt.figure()
frames = []
done = 0
eps = 5

while done < eps:
    im = plt.imshow(obs[0].astype(np.uint8), animated=True)
    frames.append([im])
    actions, values, states, neglogpacs = final_model.step(obs)
    obs[:], rewards, dones, infos = venv.step(actions)
    done += dones[0]

ani = animation.ArtistAnimation(fig, frames, interval=500, blit=True,
                                repeat_delay=1000)

ani.save(osp.join(LOG_DIR, 'maze.gif'), writer=PillowWriter(fps=20))

plt.show()
