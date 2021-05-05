from __future__ import annotations
import numpy as np
from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass
from amazons.constants import *
import pygame.draw
from pathlib import Path


@dataclass
class Coordinate:
    """ Class for keeping track of coordinates on a board"""
    x: int
    y: int

    def is_on_board(self, board: Board) -> bool:
        return (0 <= self.x < board.width) and (0 <= self.y < board.height)

    def __sub__(self, other: Coordinate) -> Distance:
        return Distance(self.x - other.x, self.y - other.y)

    def __add__(self, other: Distance) -> Coordinate:
        return Coordinate(self.x + other.x, self.y + other.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


@dataclass
class Distance:
    """ Class to represent the distance between two coordinates in a board"""
    x: int
    y: int

    @property
    def unit_step(self) -> Distance:
        """Gets the unit step of a distance
        :return: a Distance that moves by one square in the direction of the distance
        """
        if self.is_horizontal() or self.is_vertical() or self.is_diagonal():
            return Distance(np.sign(self.x), np.sign(self.y))
        else:
            raise RuntimeError("Cannot compute unit step for a move that isn't horizontal, vertical, or diagonal.")

    def is_horizontal(self) -> bool:
        """Determines if a distance is purely horizontal movement
        :return: True if moving horizontally, otherwise False
        """
        return (self.x != 0) and (self.y == 0)

    def is_vertical(self) -> bool:
        """Determines if a distance is purely vertical movement
        :return: True if moving vertically, otherwise False
        """
        return (self.x == 0) and (self.y != 0)

    def is_diagonal(self) -> bool:
        """Determines if a distance is purely diagonal (like a bishop moves in chess)
        :return: True if diagonal, otherwise false
        """
        return (self.x != 0) and (self.y != 0) and np.abs(self.x) == np.abs(self.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class Board:
    """ Class for representing a generic Game of the Amazons Board"""
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self._state: np.ndarray = np.zeros((self.height, self.width), dtype=np.uint8)

    def __str__(self) -> str:
        out: str = ""
        for row in self._state:
            for value in row:
                out += SYMBOLS[value]
            out += "\n"
        return out

    def square_is_empty(self, coordinate: Coordinate) -> bool:
        """Check if a square is empty
        :param coordinate: which square to check
        :return: True if square is empty, false otherwise
        """
        assert coordinate.is_on_board(self)
        return self._state[coordinate.y, coordinate.x] == EMPTY

    def set_square_value(self, coordinate: Coordinate, value: int) -> None:
        assert value in [EMPTY, BURNT, WHITE_AMAZON, BLACK_AMAZON]
        self._state[coordinate.y, coordinate.x] = value

    def get_square_value(self, coordinate: Coordinate) -> int:
        """Gets the value of a square
        :param coordinate: which square to get value of
        :return: 0 if empty, 1 if burnt, 2 if white amazon, 3 if black amazon
        """
        assert coordinate.is_on_board(self)
        return self._state[coordinate.y, coordinate.x]

    # def is_valid_move(self, start: Coordinate, end: Coordinate, burn: Coordinate) -> bool:
    #     """
    #     Determines if a move is valid
    #     :param start: square to start moving the Amazon from
    #     :param end: square to end moving the Amazon to
    #     :param burn: square to fire Amazon arrow and burn for the rest of the game
    #     :return: True if the move is valid, false otherwise
    #     """
    #     # A boolean we will pass through to determine if the move is valid
    #     is_valid = True
    #
    #     # Check that the three squares are valid squares
    #     start_square_is_on_board: bool = start.is_on_board(self)
    #     end_square_is_on_board: bool = end.is_on_board(self)
    #     burn_square_is_on_board: bool = burn.is_on_board(self)
    #     is_valid &= start_square_is_on_board
    #     is_valid &= end_square_is_on_board
    #     is_valid &= burn_square_is_on_board
    #
    #     # Check that the start square is indeed an Amazon
    #     start_square_is_amazon: bool = (self.get_square_value(start) == WHITE_AMAZON) or \
    #                                    (self.get_square_value(start) == BLACK_AMAZON)
    #     is_valid &= start_square_is_amazon
    #
    #     # check if path between the start and end squares are empty
    #     is_valid &= self._empty_between_squares(start, end)
    #
    #     # check if the path between the end and burn squares is empty
    #     is_valid &= self._empty_between_squares(end, burn)
    #
    #     return is_valid

    def _empty_between_squares(self, start: Coordinate, end: Coordinate, inclusive: bool = False) -> bool:
        """Determine if the path between two squares is empty
        :param start: where to start checking
        :param end: where to stop checking
        :param inclusive: if True, include the start and end point in check, otherwise only check the squares between
        :return: True if the path between two squares is empty, otherwise False
        """
        is_empty = True
        current_square = start
        unit_step: Distance = (start - end).unit_step
        while current_square != end:
            current_square += unit_step
            is_empty &= self.get_square_value(current_square) == EMPTY

        if inclusive:
            is_empty &= self.get_square_value(start) == EMPTY
            is_empty &= self.get_square_value(end) == EMPTY
        return is_empty

    def move(self, start: Coordinate, end: Coordinate, burn: Coordinate) -> None:
        """Moves an Amazon and burns a square as well
        :param start: square to start moving the Amazon from
        :param end: square to end moving the Amazon to
        :param burn: square to fire Amazon arrow and burn for the rest of the game
        """
        # assert self.is_valid_move(start, end, burn)
        value = self.get_square_value(start)
        self.set_square_value(start, EMPTY)
        self.set_square_value(end, value)
        self.set_square_value(burn, BURNT)

    def get_white_amazon_positions(self):
        return np.where(self._state == WHITE_AMAZON)

    def get_black_amazon_positions(self):
        return np.where(self._state == BLACK_AMAZON)