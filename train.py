import os.path as osp
import os

import gym
import numpy as np
import tensorflow as tf
from baselines import logger
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

learning_rate = 5e-4
ent_coef = .01
gamma = .999
total_time = int(2e6)
lam = .95
nsteps = 256
nminibatches = 8
ppo_epochs = 3
clip_range = .2
use_vf_clipping = True

format_strs = ['csv', 'stdout']
logger.configure(dir=LOG_DIR, format_strs=format_strs)

logger.info("creating environment")
def env_fn():
    return gym.make('maze-v0', start_level=0, num_levels=50)
envs = [env_fn for x in range(64)]
venv = DummyVecEnv(envs)

def eval_env_fn():
    return gym.make('maze-v0', start_level=0, num_levels=0)
eval_envs = [eval_env_fn for x in range(64)]
eval_venv = DummyVecEnv(eval_envs)

venv = VecMonitor(
    venv=venv, filename=None, keep_buf=100,
)

eval_venv = VecMonitor(
    venv=eval_venv, filename=None, keep_buf=100,
)

logger.info("creating tf session")
config = tf.ConfigProto()
sess = tf.Session(config=config)
sess.__enter__()

conv_fn = lambda x: build_impala_cnn(x, depths=[16,32,32], emb_size=256)

logger.info("training")
final_model = ppo2.learn(
    env=venv,
    eval_env=eval_venv,
    network=conv_fn,
    total_timesteps=total_time,
    save_interval=0,
    nsteps=nsteps,
    nminibatches=nminibatches,
    lam=lam,
    gamma=gamma,
    noptepochs=ppo_epochs,
    log_interval=1,
    ent_coef=ent_coef,
    mpi_rank_weight=0,
    clip_vf=use_vf_clipping,
    lr=learning_rate,
    cliprange=clip_range,
    update_fn=None,
    init_fn=None,
    vf_coef=0.5,
    max_grad_norm=0.5,
)

savepath = osp.join(logger.get_dir(), 'final')
final_model.save(savepath)
