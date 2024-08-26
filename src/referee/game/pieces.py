# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass
from enum import Enum
from typing import Collection

from .constants import BOARD_N
from .coord import Vector2, Coord


class PieceType(Enum):
    """
    An `enum` capturing the nineteen different types of fixed tetromino pieces.
    """
    O           = "O"
    IHorizontal = "I-H"
    IVertical   = "I-V"
    TUp         = "T-U"
    TRight      = "T-R"
    TDown       = "T-D"
    TLeft       = "T-L"
    LUp         = "L-U"
    LRight      = "L-R"
    LDown       = "L-D"
    LLeft       = "L-L"
    JUp         = "J-U"
    JRight      = "J-R"
    JDown       = "J-D"
    JLeft       = "J-L"
    SHorizontal = "S-H"
    SVertical   = "S-V"
    ZHorizontal = "Z-H"
    ZVertical   = "Z-V"


_TEMPLATES = {
    PieceType.O: [
        Vector2(0, 0),
        Vector2(0, 0).right(1),
        Vector2(0, 0).down(1),
        Vector2(0, 0).right(1).down(1)
    ],
    PieceType.IHorizontal: [
        Vector2(0, 0),
        Vector2(0, 0).right(1),
        Vector2(0, 0).right(2),
        Vector2(0, 0).right(3)
    ],
    PieceType.IVertical: [
        Vector2(0, 0),
        Vector2(0, 0).down(1),
        Vector2(0, 0).down(2),
        Vector2(0, 0).down(3)
    ],
    PieceType.TUp: [
        Vector2(0, 0),
        Vector2(0, 0).up(1),
        Vector2(0, 0).up(1).right(1),
        Vector2(0, 0).up(1).left(1)
    ],
    PieceType.TRight: [
        Vector2(0, 0),
        Vector2(0, 0).right(1),
        Vector2(0, 0).right(1).down(1),
        Vector2(0, 0).right(1).up(1)
    ],
    PieceType.TDown: [
        Vector2(0, 0),
        Vector2(0, 0).down(1),
        Vector2(0, 0).down(1).left(1),
        Vector2(0, 0).down(1).right(1)
    ],
    PieceType.TLeft: [
        Vector2(0, 0),
        Vector2(0, 0).left(1),
        Vector2(0, 0).left(1).up(1),
        Vector2(0, 0).left(1).down(1)
    ],
    PieceType.LUp: [
        Vector2(0, 0),
        Vector2(0, 0).left(1),
        Vector2(0, 0).left(1).up(1),
        Vector2(0, 0).left(1).up(2),
    ],
    PieceType.LRight: [
        Vector2(0, 0),
        Vector2(0, 0).up(1),
        Vector2(0, 0).up(1).right(1),
        Vector2(0, 0).up(1).right(2),
    ],
    PieceType.LDown: [
        Vector2(0, 0),
        Vector2(0, 0).right(1),
        Vector2(0, 0).right(1).down(1),
        Vector2(0, 0).right(1).down(2),
    ],
    PieceType.LLeft: [
        Vector2(0, 0),
        Vector2(0, 0).down(1),
        Vector2(0, 0).down(1).left(1),
        Vector2(0, 0).down(1).left(2),
    ],
    PieceType.JUp: [
        Vector2(0, 0),
        Vector2(0, 0).right(1),
        Vector2(0, 0).right(1).up(1),
        Vector2(0, 0).right(1).up(2),
    ],
    PieceType.JRight: [
        Vector2(0, 0),
        Vector2(0, 0).down(1),
        Vector2(0, 0).down(1).right(1),
        Vector2(0, 0).down(1).right(2),
    ],
    PieceType.JDown: [
        Vector2(0, 0),
        Vector2(0, 0).left(1),
        Vector2(0, 0).left(1).down(1),
        Vector2(0, 0).left(1).down(2),
    ],
    PieceType.JLeft: [
        Vector2(0, 0),
        Vector2(0, 0).up(1),
        Vector2(0, 0).up(1).left(1),
        Vector2(0, 0).up(1).left(2),
    ],
    PieceType.SHorizontal: [
        Vector2(0, 0),
        Vector2(0, 0).right(1),
        Vector2(0, 0).right(1).up(1),
        Vector2(0, 0).right(2).up(1),
    ],
    PieceType.SVertical: [
        Vector2(0, 0),
        Vector2(0, 0).up(1),
        Vector2(0, 0).up(1).left(1),
        Vector2(0, 0).up(2).left(1),
    ],
    PieceType.ZHorizontal: [
        Vector2(0, 0),
        Vector2(0, 0).left(1),
        Vector2(0, 0).left(1).up(1),
        Vector2(0, 0).left(2).up(1),
    ],
    PieceType.ZVertical: [
        Vector2(0, 0),
        Vector2(0, 0).down(1),
        Vector2(0, 0).down(1).left(1),
        Vector2(0, 0).down(2).left(1),
    ],
}


def piece_fingerprint(
    coords: Collection[Coord] | Collection[Vector2]
) -> str | None:
    """
    Compute a unique identifier for a piece, given a set of coords. This
    identifier is invariant under translation on a toroidal board.
    """
    min_r = min(coords, key=lambda c: c.r).r
    min_c = min(coords, key=lambda c: c.c).c

    max_r = max(coords, key=lambda c: c.r).r
    max_c = max(coords, key=lambda c: c.c).c

    # Shift the piece so that the top-left bounding box coordinate is (0, 0)
    if min_r == 0 and max_r == BOARD_N - 1:
        # Piece is wrapped around the top of the board, shift it down
        coords = [c + Vector2(BOARD_N // 2, 0) for c in coords]
        min_r = min(coords, key=lambda c: c.r).r

    if min_r != 0:
        coords = [c - Vector2(min_r, 0) for c in coords]

    if min_c == 0 and max_c == BOARD_N - 1:
        # Piece is wrapped around the left of the board, shift it right
        coords = [c + Vector2(0, BOARD_N // 2) for c in coords]
        min_c = min(coords, key=lambda c: c.c).c

    if min_c != 0:
        coords = [c - Vector2(0, min_c) for c in coords]

    return ','.join(f"{c.r}{c.c}" for c in sorted(coords))

_PIECE_TYPE_FPS = {
    piece_fingerprint(v): k for k, v in _TEMPLATES.items()
}


@dataclass
class Piece:
    """
    A dataclass representing a tetromino piece, consisting of a set of
    coordinates on the game board.
    """
    coords: Collection[Coord]

    def __post_init__(self):
        self._piece_type = self._identify_type()
        if self._piece_type == None:
            raise ValueError("Coords do not match any known piece type.")
        
    def _identify_type(self) -> PieceType | None:
        """
        Identify the type of the piece, or return None if no match is found.
        """
        fp = piece_fingerprint(self.coords)
        return _PIECE_TYPE_FPS[fp] if fp in _PIECE_TYPE_FPS else None

    def __str__(self) -> str:
        return f"Piece({self.coords})"

    def __hash__(self) -> int:
        return hash(tuple(self.coords))
    
    def __eq__(self, other: 'Piece') -> bool:
        return self.coords == other.coords
    
    @property
    def type(self) -> PieceType:
        """
        Return the type of the piece.
        """
        assert self._piece_type is not None
        return self._piece_type


def create_piece(
    piece_type: PieceType, 
    origin: Coord = Coord(0, 0)
) -> Piece:
    """
    Create a piece of the given type starting at the given origin.
    """
    return Piece(
        [origin + offset for offset in _TEMPLATES[piece_type]]
    )
