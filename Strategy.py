import random
from Board import Board

class Strategy:
    def __init__(self, depth):
        self.depth = depth

    def next_move(self, board):
        legal = board.legalMoves()
        return random.choice(legal) if legal else None

    def toInt(board):
        iBoard = 0

        for v in board.board:
            iBoard += v
            iBoard <<= 5 # bit shift by 5 since the highest theoretical score is 2^17

        return iBoard
    
    def toList(iBoard):
        board = []

        # append the values in reverse order and reverse it later
        for _ in range(16):
            v = iBoard % (2 << 5)
            board.append(v)
            iBoard >>= 5

        return board[::-1]
    
    