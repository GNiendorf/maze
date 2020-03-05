import gym
import random
import numpy as np
from gym.utils import seeding
from gym import error, spaces, utils
from .maze import generate_maze

N, S, E, W = 1, 2, 4, 8

class MazeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, start_level=0, num_levels=100, size=5, horizon=200):
        self.size = size
        self.horizon = horizon
        self.start_level = start_level
        self.num_levels = num_levels if num_levels > 0 else 1e9
        self.num_envs = 1
        self.step_dir = [[-1,0],[1,0],[0,1],[0,-1]]
        self.l = 0
        self.ep = 0
        self.R = 0

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.size+2, self.size+2, 3), dtype=np.uint8)

    def display_maze(self, agent=None, goal=None):
        low = np.ones((2,1,3), dtype=np.uint8)*255
        empty = np.ones((2,1,3), dtype=np.uint8)*255
        wall = np.ones((2,1,3), dtype=np.uint8)*255
        low[1:,:,:] = 50
        wall[:,:,:] = 50
        maze = np.repeat(wall[1:,:,:],(len(self.grid[0]) * 2 + 1), axis=1)
        for idx, row in enumerate(self.grid):
            line = wall
            for x, cell in enumerate(row):
                if (cell & S != 0):
                    line = np.hstack((line, empty))
                else:
                    line = np.hstack((line, low))
                if cell & E != 0:
                    if ((cell | row[x+1]) & S != 0):
                        line = np.hstack((line, empty))
                    else:
                        line = np.hstack((line, low))
                else:
                    line = np.hstack((line, wall))
            maze = np.vstack((maze, line))
        play = np.where(maze[:,:,0] == 255)
        x, y = play[0], play[1]
        self.xy = np.vstack((x,y)).T
        if agent is None:
            self.agent = self.xy[np.random.choice(len(self.xy))]
        if goal is None:
            self.goal = self.xy[np.random.choice(len(self.xy))]
            while np.array_equal(self.agent, self.goal):
                self.goal = self.xy[np.random.choice(len(self.xy))]
        maze[self.goal[0], self.goal[1], :] = [0, 255, 0]
        maze[self.agent[0], self.agent[1], :] = [0, 0, 255]
        return maze, play

    def step(self, action):
        self.l += 1
        reward = 0
        done = False
        old_agent = np.copy(self.agent)
        #Check if action is valid (not into a wall)
        if np.any([np.array_equal(self.agent+self.step_dir[action], x) for x in self.xy]):
            self.agent += self.step_dir[action]
        #Check if agent is at goal state or horizon
        goal_check = np.array_equal(self.agent, self.goal)
        horizon_check = self.l >= self.horizon
        if goal_check or horizon_check:
            if goal_check:
                reward = 10
                self.R += 10
            done = True
            self.reset()
        else:
            #Update frame
            self.maze[old_agent[0], old_agent[1]] = [255, 255, 255]
            self.maze[self.agent[0], self.agent[1]] = [0, 0, 255]
        info = {'seed':self.seed_num, 'episode_complete':done}
        if done:
            self.R = 0
            self.l = 0
            self.ep += 1
        return self.maze, reward, done, info

    def step_async(self, actions):
        self.obs, self.reward, self.done, self.info = self.step(actions[0])
   
    def step_wait(self):
        return self.obs, np.array([self.reward]), np.array([self.done]), np.array([self.info])

    def reset(self):
        self.seed_num = random.randint(self.start_level, self.num_levels-1)
        np.random.seed(self.seed_num)
        self.grid = generate_maze(self.size, self.seed_num)
        self.maze, self.play = self.display_maze()
        return self.maze

    def render(self, mode='human'):
        return self.maze

    def close(self):
        pass