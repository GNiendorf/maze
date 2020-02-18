import numpy as np

N, S, E, W = 1, 2, 4, 8
DX = { E : 1, W : -1, N :  0, S : 0 }
DY = { E : 0, W :  0, N : -1, S : 1 }
OPPOSITE = { E : W, W : E, N : S, S : N }

class Tree(object):
    def __init__(self):
        self.parent = None

    def root(self):
        if self.parent: return self.parent.root()
        return self

    def connected(self, tree):
        return self.root() == tree.root()

    def connect(self, tree):
        tree.root().parent = self

def display_maze(grid):
    low = np.zeros((6,3,3), dtype=int)
    empty = np.zeros((6,3,3), dtype=int)
    wall = np.zeros((6,3,3), dtype=int)
    low[3:,:,0] = 255
    wall[:,:,0] = 255
    maze = np.repeat(wall[3:,:,:],(len(grid[0]) * 2 + 1), axis=1)
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
    pad = int((64-np.shape(maze)[0])/2)
    padded_pic = np.pad(maze, ((pad,pad),(pad,pad), (0,0)), mode='edge')
    return padded_pic

def generate_maze(size):
    width=int((size+1)/2)
    height=int((size+1)/2)
    grid = [[0 for y in range(width)] for x in range(height)]
    sets = [[Tree() for y in range(width)] for x in range(height)]
    edges = []
    for y in range(height):
        for x in range(width):
            if y>0: edges.append([x, y, N])
            if x>0: edges.append([x, y, W])
    np.random.shuffle(edges)
    while len(edges) > 0:
        x, y, direction = edges.pop()
        nx, ny = x + DX[direction], y + DY[direction]
        set1, set2 = sets[y][x], sets[ny][nx]
        if not set1.connected(set2):
            set1.connect(set2)
            grid[y][x] |= direction
            grid[ny][nx] |= OPPOSITE[direction]
    return grid
