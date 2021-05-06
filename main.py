from amazons.base import Board, Coordinate
from amazons.gui import GUI
from amazons.constants import *
import pygame
from pygame.locals import *
import sys
import numpy as np


if __name__ == "__main__":
    pygame.init()
    # Setting up FPS
    FPS = 60
    clock = pygame.time.Clock()

    # Create a white screen
    display_surface = pygame.display.set_mode((800, 800))
    display_surface.fill(BLACK)
    pygame.display.set_caption("Game of the Amazons")
    print(display_surface.get_size())

    b = Board(8, 8)
    b.set_square_value(Coordinate(1, 1), BURNT)
    b.set_square_value(Coordinate(1, 2), WHITE_AMAZON)
    # b.set_square_value(Coordinate(7, 2), WHITE_AMAZON)

    # b.set_square_value(Coordinate(5, 5), WHITE_AMAZON)
    b.set_square_value(Coordinate(3, 3), BLACK_AMAZON)
    b.set_square_value(Coordinate(4, 4), BLACK_AMAZON)

    gui = GUI(b, display_surface)

    # Game Loop
    while True:
        gui.update(display_surface)
        gui.event_handler(display_surface)
        pygame.display.update()
        clock.tick(FPS)


