import random
from Board import Board
from IntBoard import IntBoard
import copy

class Strategy:

    def __init__(self, depth, sample = 8):
        self.depth = depth
        self.sample = sample
        self.snake = [16,15,14,13,9,10,11,12,8,7,6,5,1,2,3,4]

    def next_move1(self, board):
        iBoard = IntBoard.toInt(board)
        cache = {}
        cachesUsed = 0
        cachesMissed = 0

        def dfs(iBoard, depth):
            nonlocal cachesUsed, cachesMissed
            # reached max depth
            if depth == self.depth:
                return self.heuristic1(iBoard), None
            # board already calculated at a depth <= current depth
            elif iBoard in cache and cache[iBoard][1] <= depth:
                cachesUsed += 1
                return cache[iBoard][0], None
            cachesMissed += 1
            
            legal = IntBoard.legalMoves(iBoard)

            # exit early if no legal moves
            if not legal:
                return 0, None
            
            ev = 0
            bestDir = legal[0]
            bestEV = 0

            for dir in legal:
                curEV = 0

                # compute shift, then generate all spawns later to avoid recomputation of merge logic
                shiftBoard = IntBoard.shift(iBoard, dir)
                
                # compute EV of heuristic for that move
                for _ in range(self.sample):
                    newBoard = IntBoard.spawn_tile(shiftBoard)
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
        return bestMove, cachesUsed, cachesMissed
    
    def next_move2(self, board):
        cache = {}
        cachesUsed = 0
        cachesMissed = 0

        def dfs(board, depth):
            nonlocal cachesUsed, cachesMissed
            grid = tuple(board.board)

            # reached max depth
            if depth == self.depth:
                return self.heuristic2(board), None
            # board already calculated at a depth <= current depth
            elif grid in cache and cache[grid][1] <= depth:
                cachesUsed += 1
                return cache[grid][0], None
            cachesMissed += 1
            
            legal = board.legalMoves()

            # exit early if no legal moves
            if not legal:
                return 0, None
            
            ev = 0
            bestDir = legal[0]
            bestEV = 0

            for dir in legal:
                curEV = 0

                # compute EV of heuristic for that move
                shiftBoard = Board()
                shiftBoard.board = list(grid)
                shiftBoard.shift(dir)
                for _ in range(self.sample):
                    newBoard = Board()
                    newBoard.board = copy.copy(shiftBoard.board)
                    newBoard.spawn_tile()
                    val, _ = dfs(newBoard, depth + 1)
                    curEV += val

                # keep track of best move
                if curEV > bestEV:
                    bestDir = dir
                    bestEV = curEV
                
                ev += curEV / self.sample

            ev /= len(legal)
            
            cache[grid] = (ev, depth)
            return ev, bestDir

        _, bestMove = dfs(board, 0)
        return bestMove, cachesUsed, cachesMissed
    
    def heuristic1(self, iBoard):
        val = IntBoard.score(iBoard)
        # val = 0
        # for i in range(Board.SIZE ** 2):
        #     val += (2 ** IntBoard.at1(iBoard, i)) * self.snake[i]
        return val
    
    def heuristic2(self, board):
        val = board.score()
        # grid = board.board
        # maxTile = 0

        # for i in range(Board.SIZE ** 2):
        #     val += (2 ** grid[i]) * self.snake[i]
        #     maxTile = max(maxTile, grid[i])

        # for i in range(Board.SIZE ** 2):
        #     if grid[i] == 0:
        #         val += (2 ** maxTile) * maxTile
        
        return val