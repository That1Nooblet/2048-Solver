import pygame
import random
from Board import Board
from Strategy import Strategy
from collections import defaultdict

class Game2048:
    SIZE = Board.SIZE
    SCORE_HEIGHT = 60
    TILE_SIZE = 120
    GAP = 10
    PADDING = 20
    BG_COLOR = (187, 173, 160)

    COLORS = {
        0: (205, 193, 180),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
    }

    def __init__(self):
        pygame.init()

        self.width = self.PADDING * 2 + self.SIZE * self.TILE_SIZE + (self.SIZE - 1) * self.GAP
        self.height = self.width + self.SCORE_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2048")

        self.font = pygame.font.SysFont("arial", 36, bold=True)

        self.board = Board()
        self.clearBoard()
        self.running = True
        self.state = "Human"
        self.strategy = Strategy(1)
        
        # key map for key handler and history logic
        self.key_map = defaultdict()
        
        self.key_map[pygame.K_LEFT] = lambda : self.makeMove(Board.LEFT)
        self.key_map[pygame.K_RIGHT] = lambda : self.makeMove(Board.RIGHT)
        self.key_map[pygame.K_UP] = lambda : self.makeMove(Board.UP)
        self.key_map[pygame.K_DOWN] = lambda : self.makeMove(Board.DOWN)
        self.key_map[pygame.K_r] = lambda : self.clearBoard()
        self.key_map[pygame.K_u] = lambda : self.undo()
        self.key_map[pygame.K_h] = lambda : self.printHist()
        self.key_map[pygame.K_a] = lambda : self.switchState()
        self.key_map[pygame.K_m] = lambda : self.stratMove()

    # board index helper

    def index(self, r, c):
        return r * self.SIZE + c
    
    # history logic
    def addHist(self, newHist):
        if newHist: self.history += newHist
    
    def makeMove(self, dir):
        self.addHist(self.board.move(dir))

    def clearBoard(self):
        self.history = [self.board.reset()]

    def undo(self):
        if (len(self.history) > 2):
            self.board.board = list(self.history[-3][1])
            self.history.pop()
            self.history.pop()
    
    def printHist(self):
        print(f"History Length: {len(self.history)}")
        for type, board in self.history:
            print(f"Type: {type}, {board}")

    # AI logic

    def switchState(self):
        if self.state == "Human": self.state = "AI"
        elif self.state == "AI": self.state = "Human"

    def stratMove(self):
        move = self.strategy.next_move(self.board)
        if move: self.makeMove(move)

    # handlers

    def key_handler(self, key):
        self.key_map.get(key, lambda: None)()

    def mouse_handler(self, pos, button):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.key_handler(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_handler(event.pos, event.button)

    # draw handler

    def draw(self):
        self.screen.fill(self.BG_COLOR)

        # display score
        score_text = self.font.render(
            f"Score: {self.board.score()}",
            True,
            (119, 110, 101)
        )
        self.screen.blit(
            score_text,
            (self.PADDING, self.PADDING // 2)
        )

        # display board
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                powVal = self.board.at(r,c)
                value = 1 << powVal if powVal else 0
                color = self.COLORS.get(value, (60, 58, 50))

                x = self.PADDING + c * (self.TILE_SIZE + self.GAP)
                y = self.PADDING + r * (self.TILE_SIZE + self.GAP) + self.SCORE_HEIGHT

                rect = pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect, border_radius=8)

                if value:
                    text = self.font.render(str(value), True, (0, 0, 0))
                    self.screen.blit(text, text.get_rect(center=rect.center))

        pygame.display.flip()

# main game loop
def main():
    game = Game2048()
    clock = pygame.time.Clock()

    while game.running:
        game.handle_events()
        game.draw()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()