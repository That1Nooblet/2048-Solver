import random
from Board import Board
from IntBoard import IntBoard

class Strategy:

    def __init__(self, depth, sample = 8):
        self.depth = depth
        self.sample = sample

    def next_move(self, board):
        iBoard = IntBoard.toInt(board)
        cache = {}

        def dfs(iBoard, depth):
            # reached max depth
            if depth == self.depth:
                return self.heuristic(iBoard), None
            # board already calculated at a depth <= current depth
            elif iBoard in cache and cache[iBoard][1] <= depth:
                return cache[iBoard][0], None
            
            legal = IntBoard.legalMoves(iBoard)

            # exit early if no legal moves
            if not legal:
                return 0, None
            
            ev = 0
            bestDir = legal[0]
            bestEV = 0

            for dir in legal:
                curEV = 0

                # compute EV of heuristic for that move
                for _ in range(self.sample):
                    newBoard = IntBoard.move(iBoard, dir)
                    val, _ = dfs(newBoard, depth + 1)
                    curEV += val

                # keep track of best move
                if curEV > bestEV:
                    bestDir = dir
                    bestEV = curEV
                
                ev += curEV / self.sample

            ev /= len(legal)
            
            cache[iBoard] = (ev, depth)
            return ev, bestDir

        _, bestMove = dfs(iBoard, 0)
        return bestMove
    
    def heuristic(self, iBoard):
        return IntBoard.score(iBoard)