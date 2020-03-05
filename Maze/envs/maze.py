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

def generate_maze(size, seed):
    np.random.seed(seed)
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
