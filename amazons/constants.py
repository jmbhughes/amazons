from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional

# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (200, 200, 200)
DARK_RED = (97, 17, 0)

EMPTY: int = 0
BURNT: int = 1
WHITE_AMAZON: int = 2
BLACK_AMAZON: int = 3
SYMBOLS: Dict[int, str] = {EMPTY: "□",
                           BURNT: "■",
                           WHITE_AMAZON: "W",
                           BLACK_AMAZON: "B"}