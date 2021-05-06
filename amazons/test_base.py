from unittest import TestCase
from amazons.base import Board, Coordinate
from amazons.constants import *


class TestBoard(TestCase):
    def test_square_is_empty(self):
        b = Board(10, 10)
        self.assertTrue(b.square_is_empty(Coordinate(1, 1)))

    def test_empty_between_squares(self):
        b = Board(10, 10)
        b.set_square_value(Coordinate(1, 1), BURNT)
        b.set_square_value(Coordinate(5, 5), BURNT)
        b.set_square_value(Coordinate(9, 9), WHITE_AMAZON)

        self.assertTrue(b.empty_between_squares(Coordinate(2, 2), Coordinate(2, 4)))
        self.assertFalse(b.empty_between_squares(Coordinate(5, 4), Coordinate(5, 6)))
        self.assertFalse(b.empty_between_squares(Coordinate(5, 5), Coordinate(5, 8), include_start=True))
        self.assertFalse(b.empty_between_squares(Coordinate(5, 1), Coordinate(5, 5), include_end=True))
        self.assertTrue(b.empty_between_squares(Coordinate(6, 6), Coordinate(8, 8),
                                                include_start=True, include_end=True))
        self.assertFalse(b.empty_between_squares(Coordinate(6, 6), Coordinate(9, 9),
                                                 include_start=True, include_end=True))


class TestCoordinate(TestCase):
    def test_is_on_board(self):
        b = Board(10, 10)
        self.assertTrue(Coordinate(1, 1).is_on_board(b))
        self.assertTrue(Coordinate(2, 2).is_on_board(b))
        self.assertFalse(Coordinate(10, 1).is_on_board(b))
        self.assertFalse(Coordinate(-1, 1).is_on_board(b))

    def test_sub(self):
        c = Coordinate(1, 2)
