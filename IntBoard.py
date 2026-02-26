import random
from Board import Board

class IntBoard:

    # represents the board as an integer, using only 5 bits per tile to save memory

    @staticmethod
    def toInt(board):
        iBoard = 0

        for v in board.board:
            iBoard <<= 5 # bit shift by 5 since the highest theoretical score is 2^17
            iBoard += v

        return iBoard
    
    @staticmethod
    def toList(iBoard):
        board = []

        # append the values in reverse order and reverse it later
        for _ in range(Board.SIZE ** 2):
            v = iBoard % (1 << 5)
            board.append(v)
            iBoard >>= 5

        return board[::-1]
    
    # logic with integer board

    @staticmethod
    def index(r, c):
        return r * Board.SIZE + c
    
    @staticmethod
    def bitPush(idx):
        return 5 * (Board.SIZE ** 2 - 1 - idx)
    
    @staticmethod
    def at1(iBoard, i):
        return (iBoard >> (IntBoard.bitPush(i))) % (1 << 5)

    @staticmethod
    def at2(iBoard, r, c):
        i = IntBoard.index(r, c)
        return IntBoard.at1(iBoard, i)
    
    @staticmethod
    def update1(iBoard, val, i):
        iBoard -= IntBoard.at1(iBoard, i) << IntBoard.bitPush(i)
        iBoard += val << IntBoard.bitPush(i)
        return iBoard
    
    @staticmethod
    def update2(iBoard, val, r, c):
        idx = IntBoard.index(r, c)
        return IntBoard.update1(iBoard, val, idx)
    
    @staticmethod
    def lineBitPush(idx):
        return 5 * (Board.SIZE - 1 - idx)
    
    @staticmethod
    def lineAt(line, i):
        return (line >> (IntBoard.lineBitPush(i))) % (1 << 5)
    
    @staticmethod
    def lineUpd(line, val, i):
        line -= IntBoard.lineAt(line, i) << IntBoard.lineBitPush(i)
        line += val << IntBoard.lineBitPush(i)
        return line
    
    # game logic

    @staticmethod
    def spawn_tile(iBoard):
        empty = []
        for r in range(Board.SIZE):
            for c in range(Board.SIZE):
                p = r * Board.SIZE + c
                if IntBoard.at2(iBoard, r, c) == 0:
                    empty.append(p)

        if empty:
            p = random.choice(empty)
            newVal = 1 if random.random() < 0.9 else 2
            iBoard = IntBoard.update1(iBoard, newVal, p)
            return iBoard
        
        return iBoard

    @staticmethod
    def legalMoves(iBoard):
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
                    line += IntBoard.at2(iBoard, place, i)
                return reverseLine(line) if dir == Board.LEFT else line
            else:
                line = 0
                for i in range(Board.SIZE):
                    line <<= 5
                    line += IntBoard.at2(iBoard, i, place)
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
    
    @staticmethod
    def shift(iBoard, dir):
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
                    line += IntBoard.at2(iBoard, place, i)
                return reverseLine(line) if dir == Board.RIGHT else line
            else:
                line = 0
                for i in range(Board.SIZE):
                    line <<= 5
                    line += IntBoard.at2(iBoard, i, place)
                return reverseLine(line) if dir == Board.DOWN else line
            
        def compressAndMerge(line):
            new = 0
            found = 0
            for i in range(Board.SIZE):
                val = IntBoard.lineAt(line, i)
                if val:
                    new = IntBoard.lineUpd(new, val, found)
                    found += 1

            merged = 0
            mi = 0 # merged index
            i = 0 # new index
            while i < found:
                current = IntBoard.lineAt(new, i)
                if i + 1 < found and current == IntBoard.lineAt(new, i+1):
                    val = current + 1
                    merged = IntBoard.lineUpd(merged, val, mi)
                    i += 2
                else:
                    val = current
                    merged = IntBoard.lineUpd(merged, val, mi)
                    i += 1
                mi += 1

            return merged
        
        def setLine(iBoard, line, i):
            if dir in (Board.RIGHT, Board.DOWN):
                line = reverseLine(line)

            if dir in (Board.LEFT, Board.RIGHT):
                for c in range(Board.SIZE):
                    lineVal = IntBoard.lineAt(line, c)
                    iBoard = IntBoard.update2(iBoard, lineVal, i, c)
            else:
                for r in range(Board.SIZE):
                    lineVal = IntBoard.lineAt(line, r)
                    iBoard = IntBoard.update2(iBoard, lineVal, r, i)
            
            return iBoard
        
        for i in range(Board.SIZE):
            original = getLine(i)
            merged = compressAndMerge(original)
            iBoard = setLine(iBoard, merged, i)

        return iBoard
    
    @staticmethod
    def move(iBoard, dir):
        iBoard = IntBoard.shift(iBoard, dir)
        iBoard = IntBoard.spawn_tile(iBoard)
        return iBoard
    
    @staticmethod
    def score(iBoard):
        total = 0

        for i in range(Board.SIZE ** 2):
            v = IntBoard.at1(iBoard, i)
            if v: total += (1 << v) * (v - 1)

        return total