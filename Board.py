import random

class Board:
    SIZE = 4
    START = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SPAWN = 5

    def __init__(self):
        self.reset()

    # board indexing helpers
    
    def index(self, r, c):
        return r * Board.SIZE + c
    
    def at(self, r, c):
        return self.board[self.index(r,c)]
    
    # game logic

    def reset(self):
        self.board = [0] * (Board.SIZE * Board.SIZE)
        self.spawn_tile()
        self.spawn_tile()
        self.history = [(Board.START, tuple(self.board))]
    
    def spawn_tile(self):
        empty = [i for i, v in enumerate(self.board) if v == 0]
        if empty:
            i = random.choice(empty)
            self.board[i] = 1 if random.random() < 0.9 else 2
            self.history.append((Board.SPAWN, tuple(self.board)))

    def compress_and_merge(self, line):
        new = [x for x in line if x != 0]
        merged = []

        i = 0
        while i < len(new):
            if i + 1 < len(new) and new[i] == new[i + 1]:
                merged.append(new[i] + 1)
                i += 2
            else:
                merged.append(new[i])
                i += 1

        merged += [0] * (Board.SIZE - len(merged))
        return merged
    
    def move(self, direction):
        moved = False

        def get_line(i):
            if direction in (Board.LEFT, Board.RIGHT):
                row = self.board[i*Board.SIZE:(i+1)*Board.SIZE]
                return row[::-1] if direction == Board.RIGHT else row
            else:
                col = [self.board[self.index(r, i)] for r in range(Board.SIZE)]
                return col[::-1] if direction == Board.DOWN else col

        def set_line(i, line):
            nonlocal moved
            if direction in (Board.RIGHT, Board.DOWN):
                line = line[::-1]

            if direction in (Board.LEFT, Board.RIGHT):
                for c in range(Board.SIZE):
                    idx = self.index(i, c)
                    if self.board[idx] != line[c]:
                        moved = True
                    self.board[idx] = line[c]
            else:
                for r in range(Board.SIZE):
                    idx = self.index(r, i)
                    if self.board[idx] != line[r]:
                        moved = True
                    self.board[idx] = line[r]

        for i in range(Board.SIZE):
            original = get_line(i)
            merged = self.compress_and_merge(original)
            set_line(i, merged)

        if moved:
            self.history.append((direction, tuple(self.board)))
            self.spawn_tile()

    def score(self):
        total = 0

        for pow in self.board:
            if pow:
                total += (1 << pow) * (pow - 1)
        
        return total