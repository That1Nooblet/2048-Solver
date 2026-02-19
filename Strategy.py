import random
from Board import Board

class Strategy:

    def __init__(self, depth):
        self.depth = depth

    def next_move(self, board):
        legal = board.legalMoves()
        return random.choice(legal) if legal else None

    # represents the board as an integer, using only 5 bits per tile to save memory

    def toInt(self, board):
        iBoard = 0

        for v in board.board:
            iBoard <<= 5 # bit shift by 5 since the highest theoretical score is 2^17
            iBoard += v

        return iBoard
    
    def toList(self, iBoard):
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
        return 5 * (Board.SIZE ** 2 - 1 - idx)
    
    def at1(self, iBoard, i):
        return (iBoard >> (self.bitPush(i))) % (1 << 5)

    def at2(self, iBoard, r, c):
        i = self.index(r, c)
        return self.at1(iBoard, i)
    
    def update1(self, iBoard, val, i):
        iBoard -= self.at1(iBoard, i) << self.bitPush(i)
        iBoard += val << self.bitPush(i)
        return iBoard
    
    def update2(self, iBoard, val, r, c):
        idx = self.index(r, c)
        return self.update1(iBoard, val, idx)
    
    def lineBitPush(self, idx):
        return 5 * (Board.SIZE - 1 - idx)
    
    def lineAt(self, line, i):
        return (line >> self.lineBitPush(i)) % (1 << 5)
    
    def lineUpd(self, line, val, i):
        line -= self.lineAt(line, i) << self.lineBitPush(i)
        line += val << self.lineBitPush(i)
        return line
    
    # game logic

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
            iBoard = self.update1(iBoard, newVal, p)
            return iBoard
        
    def legalMoves(self, iBoard):
        def reverseLine(line):
            newLine = 0
            for i in range(Board.SIZE):
                newLine <<= 5
                newLine += line % (1 << 5)
                line >>= 5
            
            return newLine

        def getLine(dir, place):
            # creates lines in reverse order so we must reverse when 
            # the direction is LEFT or UP
            if dir in (Board.LEFT, Board.RIGHT):
                line = 0
                for i in range(Board.SIZE):
                    line <<= 5
                    line += self.at2(iBoard, place, i)
                return reverseLine(line) if dir == Board.LEFT else line
            else:
                line = 0
                for i in range(Board.SIZE):
                    line <<= 5
                    line += self.at2(iBoard, i, place)
                return reverseLine(line) if dir == Board.UP else line
        
        def checkLine(line):
            foundEmpty = False
            prevVal = -1
            for i in range(Board.SIZE):
                val = (line >> (i * 5)) % (1 << 5)
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
    
    def move(self, iBoard, dir):
        moved = False

        def reverseLine(line):
            newLine = 0
            for i in range(Board.SIZE):
                newLine <<= 5
                newLine += line % (1 << 5)
                line >>= 5
            
            return newLine

        def getLine(place):
            if dir in (Board.LEFT, Board.RIGHT):
                line = 0
                for i in range(Board.SIZE):
                    line <<= 5
                    line += self.at2(iBoard, place, i)
                return reverseLine(line) if dir == Board.RIGHT else line
            else:
                line = 0
                for i in range(Board.SIZE):
                    line <<= 5
                    line += self.at2(iBoard, i, place)
                return reverseLine(line) if dir == Board.DOWN else line
            
        def compressAndMerge(line):
            new = 0
            found = 0
            for i in range(Board.SIZE):
                val = self.lineAt(line, i)
                if val:
                    new = self.lineUpd(new, val, found)
                    found += 1

            merged = 0
            mi = 0 # merged index
            i = 0 # new index
            while i < found:
                current = self.lineAt(new, i)
                if i + 1 < found and current == self.lineAt(new, i+1):
                    val = current + 1
                    merged = self.lineUpd(merged, val, mi)
                    i += 2
                else:
                    val = current
                    merged = self.lineUpd(merged, val, mi)
                    i += 1
                mi += 1

            return merged
        
        def setLine(iBoard, line, i):
            nonlocal moved
            if dir in (Board.RIGHT, Board.DOWN):
                line = reverseLine(line)

            if dir in (Board.LEFT, Board.RIGHT):
                for c in range(Board.SIZE):
                    if self.at2(iBoard, i, c) != self.lineAt(line, c):
                        moved = True
                    lineVal = self.lineAt(line, c)
                    iBoard = self.update2(iBoard, lineVal, i, c)
            else:
                for r in range(Board.SIZE):
                    if self.at2(iBoard, r, i) != self.lineAt(line, r):
                        moved = True
                    lineVal = self.lineAt(line, r)
                    iBoard = self.update2(iBoard, lineVal, r, i)
            
            return iBoard
        
        for i in range(Board.SIZE):
            original = getLine(i)
            merged = compressAndMerge(original)
            iBoard = setLine(iBoard, merged, i)
        
        if moved:
            iBoard = self.spawn_tile(iBoard)

        return iBoard
    
    def score(self, iBoard):
        total = 0

        for i in range(Board.SIZE ** 2):
            v = self.at1(iBoard, i)
            if v: total += (1 << v) * (v - 1)

        return total