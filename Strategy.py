import random
from Board import Board

class Strategy:

    def __init__(self, depth):
        self.depth = depth

    def next_move(self, board):
        legal = board.legalMoves()
        return random.choice(legal) if legal else None

    # represents the board as an integer, using only 5 bits per tile to save memory

    def toInt(board):
        iBoard = 0

        for v in board.board:
            iBoard <<= 5 # bit shift by 5 since the highest theoretical score is 2^17
            iBoard += v

        return iBoard
    
    def toList(iBoard):
        board = []

        # append the values in reverse order and reverse it later
        for _ in range(Board.SIZE ** 2):
            v = iBoard % (1 << 5)
            board.append(v)
            iBoard >>= 5

        return board[::-1]
    
    # logic with integer board
    def index(self, r, c):
        return r * Board.SIZE + c
    
    def bitPush(self, idx):
        return (Board.SIZE ** 2) - (5 * idx)
    
    def at1(self, iBoard, p):
        return (iBoard >> (self.bitPush(p))) % (1 << 5)

    def at2(self, iBoard, r, c):
        p = self.index(r, c)
        return self.at1(iBoard, p)
    
    def update(self, iBoard, p, val):
        iBoard -= self.at1(iBoard, p) << self.bitPush(p)
        iBoard += val << self.bitPush(p)

    def spawn_tile(self, iBoard):
        empty = []
        for r in range(Board.SIZE):
            for c in range(Board.SIZE):
                p = r * Board.SIZE + c
                if self.at2(iBoard, r, c) == 0:
                    empty.append(p)

        if empty:
            p = random.choice(empty)
            newVal = 1 if random.random() < 0.9 else 2
            iBoard = self.update(iBoard, p, newVal)
            return iBoard
        
    def legal_moves(self, iBoard):
        def getLine(dir, place):
            if dir in (Board.LEFT, Board.RIGHT):
                idx = self.index(place, 0)
                line = iBoard >> (5 * (Board.SIZE ** 2 - Board.SIZE))
                line %= 1 << (5 * Board.SIZE)
                return line
            else:
                line = 0
                for k in range(Board.SIZE):
                    line <<= 5
                    line += self.at2(iBoard, k, place)
                return line
        
        def checkLine(line):
            foundEmpty = False
            prevVal = -1
            for i in range(Board.SIZE):
                val = self.at1(iBoard, i)
                if val != 0 and foundEmpty: return True
                elif val == prevVal: return True

                if val == 0: foundEmpty = True
                else: prevVal = val
            
            return False
        
        def checkDir(dir):
            for place in range(Board.SIZE):
                line = getLine(dir, place)
                if (checkLine(line)): return True
            
            return False
        
        legal = []
        for dir in Board.DIRECTIONS:
            if (checkDir(dir)): legal.append(dir)
        
        return legal
    
    