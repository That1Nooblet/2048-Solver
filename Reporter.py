import time
import csv
from Board import Board
from IntBoard import IntBoard
from Strategy import Strategy

# report average time per move, moves, score, 
class Reporter:

    def __init__(self):
        self.strategy = Strategy(depth = 3, sample = 8)

    def runOne(self):
        board = Board()
        data = {}

        start = time.time()
        data["Moves"] = 0
        totalHits = 0
        totalMisses = 0
        
        while board.legalMoves():
            hits, misses = self.stratMove(board)
            data["Moves"] += 1
            totalHits += hits
            totalMisses += misses

        end = time.time()
        data["Score"] = board.score()
        totalTime = end - start
        data["AvgTime"] = totalTime / data["Moves"]
        data["AvgCaches"] = totalHits / data["Moves"]
        data["HitRate"] = totalHits / (totalHits + totalMisses)

        return data
    
    def run(self, iterations):
        with open("noCache.csv", "a", newline = '') as f:
            fieldnames = ["AvgTime", "Score", "Moves", "AvgCaches", "HitRate"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # writer.writeheader()
            for _ in range(iterations):
                data = self.runOne()
                writer.writerow(data)

    def stratMove(self, board):
        dir, cachesUsed, cachesMissed = self.strategy.next_move2(board)
        if dir: board.move(dir)
        return cachesUsed, cachesMissed

def main():
    report = Reporter()
    report.run(5)

if __name__ == "__main__":
    main()