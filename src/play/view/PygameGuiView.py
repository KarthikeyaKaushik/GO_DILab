import numpy as np
import pygame
from pygame import gfxdraw
import sys
from src.play import ConsoleView
from src.play.view import View
from src.play.view import Move
from src.play.model.Game import BLACK
from src.play.model.Game import WHITE

brown = (165, 42, 42)
black = (0, 0, 0)
white = (255, 255, 255)
size = (500, 500)
board_size = 400
offset = 50
stone_radius = 20


class PygameGuiView(View):

    def __init__(self, game):
        View.__init__(self, game)
        self.console_view = ConsoleView(game)
        self.running = False
        self.cell_size = board_size / (self.game.size - 1)

    def open(self, game_controller):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Go')
        self.console_view.print_board()
        self.render()

        while self.running:
            event = pygame.event.poll()
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                col = int(round((x - offset) / self.cell_size))
                row = int(round((y - offset) / self.cell_size))
                if 0 < col < self.game.size and 0 < row < self.game.size:
                    game_controller.current_player.receive_next_move_from_gui(Move(col, row))
            if event.type == pygame.QUIT:
                self.running = False

        # this exiting mechanism doesn't work (on macOS at least), causes a freeze TODO
        pygame.quit()
        sys.exit(0)

    def show_player_turn_start(self, name):
        self.console_view.show_player_turn_start(name)

    def show_player_turn_end(self, name):
        self.console_view.show_player_turn_end(name)
        self.render()

    def render(self):
        # board
        self.screen.fill(brown)
        for i in range(0, self.game.size):
            # horizontals
            pygame.draw.line(self.screen, black, [offset, offset + i * self.cell_size],
                             [offset + board_size, offset + i * self.cell_size], 1)
            # verticals
            pygame.draw.line(self.screen, black, [offset + i * self.cell_size, offset],
                             [offset + i * self.cell_size, offset + board_size], 1)
        # stones
        b = self.game.board.copy()  # is it necessary to copy it?
        b[b == BLACK] = 2
        b[b == WHITE] = 3
        black_rows, black_cols = np.where(b == 2)
        white_rows, white_cols = np.where(b == 3)
        for i in range(0, len(black_rows)):
            indices = black_cols[i], black_rows[i]
            self.draw_stone(indices, black)
        for i in range(0, len(white_rows)):
            indices = white_cols[i], white_rows[i]
            self.draw_stone(indices, white)

        pygame.display.flip()  # update the screen

    def draw_stone(self, indices, col):
        x = int(offset + self.cell_size * indices[0])
        y = int(offset + indices[1] * self.cell_size)
        # antialiasing via stackoverflow.com/a/26774279/2474159
        pygame.gfxdraw.aacircle(self.screen, x, y, stone_radius, col)
        pygame.gfxdraw.filled_circle(self.screen, x, y, stone_radius, col)

    def show_error(self, msg):
        self.console_view.show_error(msg)
