import gym
from gym.utils import seeding
from gym import error, spaces, utils
from .maze import generate_maze

class MazeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, start_level=0, num_levels=100):
        self.step_dir = [[-1,0],[1,0],[0,1],[0,-1]]

    def display_maze(grid, agent=None, goal=None):
        low = np.ones((2,1,3), dtype=int)*255
        empty = np.ones((2,1,3), dtype=int)*255
        wall = np.ones((2,1,3), dtype=int)*255
        low[1:,:,:] = 50
        wall[:,:,:] = 50
        maze = np.repeat(wall[1:,:,:],(len(grid[0]) * 2 + 1), axis=1)
        for idx, row in enumerate(grid):
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
        if agent is not None:
            maze[agent[0], agent[1], :] = [0, 0, 255]
        if goal is not None:
            maze[goal[0], goal[1], :] = [0, 255, 0]
        playable = np.where(maze[:,:,0] == 255)
        return maze, playable

    def step(self, action):

    def step_async(self, actions):
        self.obs, self.reward, self.done, self.info = self.step(actions[0])
   
    def step_wait(self):
        return self.obs, np.array([self.reward]), np.array([self.done]), np.array([self.info])

    def reset(self):
        self.seed = np.random.randint(start_level, num_levels)
        np.random.seed(self.seed)
        self.grid = generate_maze(5, self.seed)
        maze, play = self.display_maze(self.grid)
        x, y = play[0], play[1]
        xy = np.vstack((x,y)).T
        self.agent = xy[np.random.choice(len(xy))]
        self.goal = xy[np.random.choice(len(xy))]
        while np.array_equal(self.agent, self.goal):
            self.goal = xy[np.random.choice(len(xy))]
        self.maze, self.play = self.display_maze(self.grid, agent=agent, goal=goal)
        return self.maze

    def render(self, mode='human'):
        return self.maze

    def close(self):
        pass
