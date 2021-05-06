from pathlib import Path
import pygame
from pygame.locals import *
from amazons.constants import *
from amazons.base import Coordinate
import numpy as np
import sys


class GUI:
    def __init__(self, board, display_surface):
        self.display_surface = display_surface
        self.board = board
        self.grid_size = int(np.min([self.display_surface.get_size()[0] / self.board.width,
                                     self.display_surface.get_size()[1] / self.board.height]))

        assets_root = Path.cwd() / "assets"
        self.white_amazon_image = pygame.image.load(assets_root / "icons8-queen-100_white.png")
        self.black_amazon_image = pygame.image.load(assets_root / "icons8-queen-100_black.png")

        self.white_amazon_rects = []
        self.black_amazon_rects = []
        self._initialize_pieces()
        self.dragging = False
        self.burning = False
        self.selected = None
        self.offset_x = 0
        self.offset_y = 0

        self.start = None
        self.end = None
        self.burn = None

    def _draw_board(self) -> None:
        for i in np.arange(0, self.board.width):
            for j in np.arange(0, self.board.height):
                x = self.grid_size * i
                y = self.grid_size * j
                pygame.draw.rect(self.display_surface,
                                 DARK_RED if self.board.get_square_value(Coordinate(i, j)) == BURNT
                                 else (LIGHT_GREY if i % 2 == j % 2 else WHITE),
                                 (x, y, self.grid_size, self.grid_size))

    def _initialize_pieces(self):
        self.white_amazon_rects = []
        self.black_amazon_rects = []

        for i, j in zip(*self.board.get_white_amazon_positions()):
            x = self.grid_size * i
            y = self.grid_size * j
            self.white_amazon_rects.append(self.display_surface.blit(self.white_amazon_image, (y, x)))

        for i, j in zip(*self.board.get_black_amazon_positions()):
            x = self.grid_size * i
            y = self.grid_size * j
            self.black_amazon_rects.append(self.display_surface.blit(self.black_amazon_image, (y, x)))

    def _draw_pieces(self):
        for rect in self.white_amazon_rects:
            self.display_surface.blit(self.white_amazon_image, rect)

        for rect in self.black_amazon_rects:
            self.display_surface.blit(self.black_amazon_image, rect)

    def _update_grid_size(self):
        self.grid_size = int(np.min([self.display_surface.get_size()[0] / self.board.width,
                                     self.display_surface.get_size()[1] / self.board.height]))
        self.white_amazon_image = pygame.transform.scale(self.white_amazon_image, (self.grid_size, self.grid_size))
        self.black_amazon_image = pygame.transform.scale(self.black_amazon_image, (self.grid_size, self.grid_size))

    def _calculate_closest_square(self, position):
        return position[0] // self.grid_size, position[1] // self.grid_size

    def _snap_selected_to_grid(self, square):
        x = self.grid_size * square[0]
        y = self.grid_size * square[1]
        self.selected.x = x
        self.selected.y = y

    def update(self, display_surface):
        self._update_grid_size()
        self._draw_board()
        self._draw_pieces()
        pygame.display.flip()

    def event_handler(self, display_surface):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if not self.burning:
                    for amazon_rect in self.white_amazon_rects + self.black_amazon_rects:
                        if amazon_rect.collidepoint(event.pos):
                            self.dragging = True
                            self.selected = amazon_rect
                            mouse_x, mouse_y = event.pos
                            self.offset_x = amazon_rect.x - mouse_x
                            self.offset_y = amazon_rect.y - mouse_y
                            self.start = self._calculate_closest_square(event.pos)
                else:  # we are burning
                    self.burn = self._calculate_closest_square(event.pos)
                    print(self.end, self.burn,
                          self.board.empty_between_squares(Coordinate(*self.end), Coordinate(*self.burn),
                                                           include_end=True))
                    if self.board.empty_between_squares(Coordinate(*self.end), Coordinate(*self.burn),
                                                        include_end=True):
                        self.board.burn(Coordinate(*self.burn))
                        self.start, self.end, self.burn = None, None, None
                        self.burning = False
                        print(self.board)
                    else:
                        self.burn = None
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    closest_square = self._calculate_closest_square(event.pos)
                    if self.board.empty_between_squares(Coordinate(*self.start), Coordinate(*closest_square),
                                                        include_end=True):
                        self._snap_selected_to_grid(closest_square)
                        self.end = closest_square
                        self.dragging = False
                        self.selected = None
                        self.burning = True
                        self.board.move(Coordinate(*self.start), Coordinate(*self.end))
                    else:
                        self._snap_selected_to_grid(self.start)
                        self.start = None
                        self.end = None
                        self.dragging = False
                        self.selected = None
                        self.burning = False
            elif event.type == MOUSEMOTION:
                if self.dragging:
                    self.selected.x = event.pos[0] + self.offset_x
                    self.selected.y = event.pos[1] + self.offset_y
                if self.burning:
                    pass
