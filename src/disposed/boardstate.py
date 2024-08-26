# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass

from referee.game.pieces import Piece, PieceType, create_piece, _TEMPLATES
from referee.game.coord import Coord, Direction
from referee.game.player import PlayerColor
from referee.game.actions import Action, PlaceAction
from referee.game.exceptions import IllegalActionException
from referee.game.constants import *

from collections import deque
from utils.constants import *
import random
import numpy as np

@ dataclass
class Board:
    """
    Bitboard representation
    """
    def __init__(self):
        self.red_board = 0 
        self.blue_board = 0
        self.game_board = 0
        self.board_mask = (1 << 121) - 1
    
    def set_cell(self, coord: Coord, player: PlayerColor):
        bit_index = coord.r * BOARD_N + coord.c
        if player == PlayerColor.RED:
            self.red_board |= 1 << bit_index
            self.game_board |= 1 << bit_index
        elif player == PlayerColor.BLUE:
            self.blue_board |= 1 << bit_index
            self.game_board |= 1 << bit_index
    
    def get_cell(self, coord: Coord):
        if self._cell_occupied(coord):
            return PlayerColor.RED if self.red_board & (1 << (coord.r * 11 + coord.c)) else PlayerColor.BLUE
        else:
            return None
    
    def _within_bounds(self, coord: Coord) -> bool:
        r, c = coord
        return 0 <= r < BOARD_N and 0 <= c < BOARD_N
    
    def _cell_occupied(self, coord: Coord) -> bool:
        return not self._cell_empty(coord)
    
    def _cell_empty(self, coord: Coord) -> bool:
        bit_index = coord.r * BOARD_N + coord.c
        return not ((self.red_board | self.blue_board) & (1 << bit_index))
    
    def _player_token_count(self, color: PlayerColor) -> int:
        if color == PlayerColor.RED:
            count = bin(self.red_board).count('1')
        else:
            count = bin(self.blue_board).count('1')
        return count
    
    def _occupied_coords(self) -> set[Coord]:
        occupied_coords = set()
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                coord = Coord(r, c)
                if self._cell_occupied(coord):
                    occupied_coords.add(coord)
        return occupied_coords

    def _player_occupied_coords(self, player: PlayerColor) -> set[Coord]:
        occupied_coords = set()
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                coord = Coord(r, c)
                if self.get_cell(coord) == player:
                    occupied_coords.add(coord)
        return occupied_coords
    
    def _empty_coords(self) -> set[Coord]:
        empty_coords = set()
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                coord = Coord(r, c)
                if self._cell_empty(coord):
                    empty_coords.add(coord)
        return empty_coords
            
    def _has_neighbour(self, coord: Coord, color: PlayerColor) -> bool:
        for direction in Direction:
            neighbour = coord + direction
            if self.get_cell(neighbour) == color:
                return True
        return False
    
    def render(self, use_color: bool=False, use_unicode: bool=False) -> str:
        """
        Returns a visualisation of the game board as a multiline string, with
        optional ANSI color codes and Unicode characters (if applicable).
        """
        def apply_ansi(str, bold=True, color=None):
            bold_code = "\033[1m" if bold else ""
            color_code = ""
            if color == "r":
                color_code = "\033[31m"
            if color == "b":
                color_code = "\033[34m"
            return f"{bold_code}{color_code}{str}\033[0m"

        output = ""
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                cell = self.get_cell(Coord(r,c))
                if cell == PlayerColor.RED or cell == PlayerColor.BLUE:
                    color = "r" if cell == PlayerColor.RED else "b"
                    text = f"{color}"
                    if use_color:
                        output += apply_ansi(text, color=color, bold=False)
                    else:
                        output += text
                else:
                    output += "."
                output += " "
            output += "\n"
        return output