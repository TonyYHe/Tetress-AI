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



@dataclass(frozen=True, slots=True)
class CellState:
    """
    A structure representing the state of a cell on the game board. A cell can
    be empty, or occupied by a player's token.
    """
    player: PlayerColor | None = None

    def __post_init__(self):
        if self.player is None:
            object.__setattr__(self, "player", None)

    def __str__(self):
        return f"CellState({self.player})"
    
    def __iter__(self):
        yield self.player


class Board:
    """
    A class representing the game board for internal use in the referee. 

    NOTE: Don't assume this class is an "ideal" board representation for your
    own agent; you should think carefully about how to design data structures
    for representing the state of a game with respect to your chosen strategy.
    This class has not been optimised beyond what is necessary for the referee.
    """
    def __init__(
        self, 
        initial_state: dict[Coord, CellState] = {},
        initial_player: PlayerColor = PlayerColor.RED,
    ):
        """
        Create a new board. It is optionally possible to specify an initial
        board state (in practice this is only used for testing).
        """
        if initial_state == {}:
            self._state: dict[Coord, CellState] = {
                Coord(r, c): CellState() 
                for r in range(BOARD_N) 
                for c in range(BOARD_N)
            }
        else:
            self._state = initial_state

        self._turn_color: PlayerColor = initial_player
        self._turn_count = 0
    
    def get_legal_actions(self) -> list[PlaceAction]:
        """
        Return the legal actions based on current state of board and player
        """
        legal_actions = set()
        visited_coords = set()
        # first action for each agent
        if self._turn_count < 2:
            if self.turn_color == PlayerColor.RED:
                return [PlaceAction(Coord(4, 4), 
                                    Coord(4, 5), 
                                    Coord(4, 6), 
                                    Coord(5, 5))]
            elif self.turn_color == PlayerColor.BLUE:
                for r in range(BOARD_N):
                    piece_coords = [Coord(r, 4), 
                             Coord(r, 5), 
                             Coord(r, 6), 
                             Coord(r + 1, 5)]
                    if all([self._cell_empty(coord) for coord in piece_coords]):
                        return [PlaceAction(Coord(r, 4), 
                                            Coord(r, 5), 
                                            Coord(r, 6), 
                                            Coord(r + 1, 5))]
        # not the first action for each agent
        else:
            for coord in self._player_occupied_coords(self._turn_color):
                adj_coords = \
                    [coord.down(), coord.up(), coord.left(), coord.right()]
                for adj_coord in adj_coords:
                    if not self._cell_empty(adj_coord) or \
                          adj_coord in visited_coords:
                        continue
                    visited_coords.add(adj_coord)
                    for piecetype in PieceType:
                        piece = _TEMPLATES[piecetype]
                        for rela_coord in piece:
                            real_piece = []
                            occupied = False
                            for target_rela_coord in piece:
                                if target_rela_coord == rela_coord:
                                    real_coord = adj_coord
                                else:
                                    real_coord = adj_coord.\
                                    __add__(target_rela_coord).__sub__(rela_coord)
                                if not self._cell_empty(real_coord):
                                    occupied = True
                                    break
                                real_piece.append(real_coord)
                            if not occupied:
                                real_piece = PlaceAction(real_piece[0],
                                                         real_piece[1], 
                                                         real_piece[2], 
                                                         real_piece[3])
                                legal_actions.add(real_piece)
        return list(legal_actions)

    def __getitem__(self, cell: Coord) -> CellState:
        """
        Return the state of a cell on the board.
        """
        if not self._within_bounds(cell):
            raise IndexError(f"Cell position '{cell}' is invalid.")
        return self._state[cell]

    def apply_action(self, action: Action):
        """
        Apply an action to a board, mutating the board state. Throws an
        IllegalActionException if the action is invalid.
        """
        match action:
            case PlaceAction():
                self._resolve_place_action(action)
            case _:
                raise IllegalActionException(
                    f"Unknown action {action}", self._turn_color)
        
        self._turn_color = self._turn_color.opponent
        self._turn_count += 1

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
                if self._cell_occupied(Coord(r, c)):
                    color = self._state[Coord(r, c)].player
                    color = "r" if color == PlayerColor.RED else "b"
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
    
    @property
    def turn_count(self) -> int:
        """
        The number of actions that have been played so far.
        """
        return self._turn_count
    
    @property
    def turn_limit_reached(self) -> bool:
        """
        True iff the maximum number of turns has been reached.
        """
        return self._turn_count >= MAX_TURNS

    @property
    def turn_color(self) -> PlayerColor:
        """
        The player whose turn it is (represented as a colour).
        """
        return self._turn_color
    
    @property
    def game_over(self) -> bool:
        """
        True iff the game is over.
        """
        if self.turn_limit_reached:
            return True
        if self._turn_count < 2:
            return False

        visited = set()
        empty_coord_clusters = dict()
        for empty_coord in self._empty_coords():
            if empty_coord in visited:
                continue
            frontier = deque([empty_coord])
            empty_coord_clusters[empty_coord] = [[], 0]
            while frontier:
                coord = frontier.popleft()
                visited.add(coord)
                empty_coord_clusters[empty_coord][0].append(coord)
                empty_coord_clusters[empty_coord][1] += 1
                adj_coords = \
                    [coord.down(), coord.up(), coord.left(), coord.right()]
                for adj_coord in adj_coords:
                    if adj_coord not in visited and self._cell_empty(adj_coord):
                        frontier.append(adj_coord)
        
        for _, (coords, length) in empty_coord_clusters.items():
            if length < 4:
                continue
            for coord in coords:
                if self._has_neighbour(coord, self._turn_color):
                    return False
    
        return True
    
    @property
    def winner_color(self) -> PlayerColor | None:
        """
        The player (color) who won the game, or None if no player has won.
        """
        if not self.game_over:
            return None
        
        if self.turn_limit_reached:
            # In this case the player with the most tokens wins, or if equal,
            # the game ends in a draw.
            red_count  = self._player_token_count(PlayerColor.RED)
            blue_count = self._player_token_count(PlayerColor.BLUE)
            balance    = red_count - blue_count

            if balance == 0:
                return None
            
            return PlayerColor.RED if balance > 0 else PlayerColor.BLUE

        else:
            # Current player cannot place any more pieces. Opponent wins.
            return self._turn_color.opponent
    
    @property
    def game_result(self):
        """Returns the utility value of the terminal node."""
        if self.winner_color == PlayerColor.RED:
            return 1
        elif self.winner_color == PlayerColor.BLUE:
            return -1
        else:
            return 0
        
    def _within_bounds(self, coord: Coord) -> bool:
        r, c = coord
        return 0 <= r < BOARD_N and 0 <= c < BOARD_N
    
    def _cell_occupied(self, coord: Coord) -> bool:
        return self._state[coord].player != None
    
    def _cell_empty(self, coord: Coord) -> bool:
        return self._state[coord].player == None
    
    def _player_token_count(self, color: PlayerColor) -> int:
        return sum(1 for cell in self._state.values() if cell.player == color)
    
    def _occupied_coords(self) -> set[Coord]:
        return set(filter(self._cell_occupied, self._state.keys()))
    
    # ==========================================================================
    # Additional private functions
    def _player_occupied_coords(self, player: PlayerColor) -> set[Coord]:
        cell_occupied_by_player = lambda x : self._state[x].player == player
        return set(filter(cell_occupied_by_player, self._state.keys()))
    
    def _empty_coords(self) -> set[Coord]:
        return set(filter(self._cell_empty, self._state.keys()))
    # ==========================================================================
    def _assert_coord_valid(self, coord: Coord):
        if type(coord) != Coord or not self._within_bounds(coord):
            raise IllegalActionException(
                f"'{coord}' is not a valid coordinate.", self._turn_color)
        
    def _assert_coord_empty(self, coord: Coord):
        if self._cell_occupied(coord):
            raise IllegalActionException(
                f"Coord {coord} is already occupied.", self._turn_color)
        
    def _assert_has_attr(self, action: Action, attr: str):
        if not hasattr(action, attr):
            raise IllegalActionException(
                f"Action '{action}' is missing '{attr}' attribute.", 
                    self._turn_color)
        
    def _has_neighbour(self, coord: Coord, color: PlayerColor) -> bool:
        for direction in Direction:
            neighbour = coord + direction
            if self._state[neighbour].player == color:
                return True
        return False

    def _parse_place_action(self, action: PlaceAction) -> Piece:
        if type(action) != PlaceAction:
            raise IllegalActionException(
                f"Action '{action}' is not a PLACE action object.", 
                    self._turn_color)
        
        self._assert_has_attr(action, "c1")
        self._assert_has_attr(action, "c2")
        self._assert_has_attr(action, "c3")
        self._assert_has_attr(action, "c4")

        has_neighbour = False
        for coord in [action.c1, action.c2, action.c3, action.c4]:
            self._assert_coord_valid(coord)
            self._assert_coord_empty(coord)
            if self._has_neighbour(coord, self._turn_color):
                has_neighbour = True

        if self._turn_count >= 2 and not has_neighbour:
            raise IllegalActionException(
                f"No coords in {action} neighbour a {self._turn_color} piece.",
                    self._turn_color)

        try:
            return Piece(action.coords)
        except ValueError as e:
            raise IllegalActionException(str(e), self._turn_color)

    def _resolve_place_action(self, action: PlaceAction):
        piece = self._parse_place_action(action)
        coords_with_piece = self._occupied_coords() | set(piece.coords)

        min_r = min(c.r for c in piece.coords)
        max_r = max(c.r for c in piece.coords)
        min_c = min(c.c for c in piece.coords)
        max_c = max(c.c for c in piece.coords)
        
        remove_r_coords = [
            Coord(r, c)
            for r in range(min_r, max_r + 1)
            for c in range(BOARD_N)
            if all(Coord(r, c) in coords_with_piece for c in range(BOARD_N))
        ]

        remove_c_coords = [
            Coord(r, c)
            for r in range(BOARD_N)
            for c in range(min_c, max_c + 1)
            if all(Coord(r, c) in coords_with_piece for r in range(BOARD_N))
        ]

        for cell in action.coords:
            self._state[cell] = CellState(self._turn_color)
        
        removed_coords = remove_r_coords + remove_c_coords

        for cell in removed_coords:
            self._state[cell] = CellState(None)    