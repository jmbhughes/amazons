from pathlib import Path
import pygame
from pygame.locals import *
from amazons.constants import *
from amazons.base import Coordinate
import numpy as np
import sys


class GUI:
    def __init__(self, board, display_surface):
        # save the board and display surface
        self.display_surface = display_surface
        self.board = board

        # calculate the grid size based on the board size and display size
        self.grid_size = int(np.min([self.display_surface.get_size()[0] / self.board.width,
                                     self.display_surface.get_size()[1] / self.board.height]))

        # load the amazon images
        assets_root = Path.cwd() / "assets"
        self.white_amazon_image = pygame.image.load(assets_root / "icons8-queen-100_white.png")
        self.black_amazon_image = pygame.image.load(assets_root / "icons8-queen-100_black.png")

        # keep track of the rectangles the represent the amazons on the board so that we can drag them
        self.white_amazon_rects = []
        self.black_amazon_rects = []
        self._initialize_pieces()

        # dragging is the state you're in when a piece has been selected but not yet placed on its end position
        self.dragging = False
        # which rectangle is selected
        self.selected = None
        # the mouse offsets for the selected rectangle
        self.offset_x = 0
        self.offset_y = 0

        # burning is the state you're in when a piece has been placed but the square to burn has not been determined yet
        self.burning = False

        # the start square
        self.start = None
        # the end square
        self.end = None
        # the selected burn square
        self.burn = None

    def _draw_board(self) -> None:
        """Draw the board """
        # simply iterates over the coordinates and draws rectangle of grid_size by grid_size with the appropriate color
        for i in np.arange(0, self.board.width):
            for j in np.arange(0, self.board.height):
                x = self.grid_size * i
                y = self.grid_size * j
                pygame.draw.rect(self.display_surface,
                                 DARK_RED if self.board.get_square_value(Coordinate(i, j)) == BURNT
                                 else (LIGHT_GREY if i % 2 == j % 2 else WHITE),
                                 (x, y, self.grid_size, self.grid_size))

    def _initialize_pieces(self):
        """Initially draw the pieces on the board"""
        self.white_amazon_rects = []
        self.black_amazon_rects = []

        # iterate over the white amazon positions and blit their images
        for i, j in zip(*self.board.get_white_amazon_positions()):
            x = self.grid_size * i
            y = self.grid_size * j
            self.white_amazon_rects.append(self.display_surface.blit(self.white_amazon_image, (y, x)))

        # iterate over the black amazon positions and blit their images
        for i, j in zip(*self.board.get_black_amazon_positions()):
            x = self.grid_size * i
            y = self.grid_size * j
            self.black_amazon_rects.append(self.display_surface.blit(self.black_amazon_image, (y, x)))

    def _draw_pieces(self):
        """Called on any piece update, draw the pieces based on their current rectangle coordinates"""
        for rect in self.white_amazon_rects:
            self.display_surface.blit(self.white_amazon_image, rect)

        for rect in self.black_amazon_rects:
            self.display_surface.blit(self.black_amazon_image, rect)

    def _update_grid_size(self):
        """Update the grid size if the display has been resized"""
        self.grid_size = int(np.min([self.display_surface.get_size()[0] / self.board.width,
                                     self.display_surface.get_size()[1] / self.board.height]))
        self.white_amazon_image = pygame.transform.scale(self.white_amazon_image, (self.grid_size, self.grid_size))
        self.black_amazon_image = pygame.transform.scale(self.black_amazon_image, (self.grid_size, self.grid_size))

    def _calculate_closest_square(self, position):
        """Determine the closest square coordinate on the board given a mouse position
        :param position: mouse position as a tuple
        :return: a tuple of the square position  # TODO: convert to Coordinate type
        """
        return position[0] // self.grid_size, position[1] // self.grid_size

    def _snap_selected_to_grid(self, square) -> None:
        """ Centers the selected rectangle to the center of the specified square
        :param square: a coordinate for a square position
        """
        x = self.grid_size * square[0]
        y = self.grid_size * square[1]
        self.selected.x = x
        self.selected.y = y

    def update(self):
        """ Called each tick to update the gui display"""
        self._update_grid_size()
        self._draw_board()
        self._draw_pieces()
        pygame.display.flip()

    def event_handler(self):
        """ Handles the control of the board """
        for event in pygame.event.get():
            # for the quit event, exit and close
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # for a left click event
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if not self.burning:  # an amazon is being selected
                    # find the appropriate amazon that ios being selected
                    for amazon_rect in self.white_amazon_rects + self.black_amazon_rects:
                        if amazon_rect.collidepoint(event.pos):
                            # save the state information about which amazon is being selected and the mouse offsets
                            self.dragging = True
                            self.selected = amazon_rect
                            mouse_x, mouse_y = event.pos
                            self.offset_x = amazon_rect.x - mouse_x
                            self.offset_y = amazon_rect.y - mouse_y
                            self.start = self._calculate_closest_square(event.pos)
                else:  # we are burning
                    # estimate the burn square
                    self.burn = self._calculate_closest_square(event.pos)
                    # if that is a valid burn square do the burn
                    if self.board.empty_between_squares(Coordinate(*self.end), Coordinate(*self.burn),
                                                        include_end=True):
                        self.board.burn(Coordinate(*self.burn))
                        self.start, self.end, self.burn = None, None, None
                        self.burning = False
                        print(self.board)
                    else:  # wasn't a valid burn square so just reset the burn and wait for another selection
                        self.burn = None
            # for a left mouse up event
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:  # an amazon has been released on its end square
                    closest_square = self._calculate_closest_square(event.pos)
                    # if the square is a valid move for the amazon
                    if self.board.empty_between_squares(Coordinate(*self.start), Coordinate(*closest_square),
                                                        include_end=True):
                        self._snap_selected_to_grid(closest_square)
                        self.end = closest_square
                        self.dragging = False
                        self.selected = None
                        self.burning = True
                        self.board.move(Coordinate(*self.start), Coordinate(*self.end))
                    else:  # the amazon was attempted to move to an illegal spot, so reset it
                        self._snap_selected_to_grid(self.start)
                        self.start = None
                        self.end = None
                        self.dragging = False
                        self.selected = None
                        self.burning = False
            # for a dragging event
            elif event.type == MOUSEMOTION:
                if self.dragging:  # someone is determining where to place an amazon
                    self.selected.x = event.pos[0] + self.offset_x
                    self.selected.y = event.pos[1] + self.offset_y
