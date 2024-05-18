# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass
import random

from referee.game.pieces import Piece, PieceType, create_piece, _TEMPLATES
from referee.game.coord import Coord, Direction
from referee.game.player import PlayerColor
from referee.game.actions import Action, PlaceAction
from referee.game.exceptions import IllegalActionException
from referee.game.constants import *



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


@dataclass(frozen=True, slots=True)
class CellMutation:
    """
    A structure representing a change in the state of a single cell on the game
    board after an action has been played.
    """
    cell: Coord
    prev: CellState
    next: CellState

    def __str__(self):
        return f"CellMutation({self.cell}, {self.prev}, {self.next})"


@dataclass(frozen=True, slots=True)
class BoardMutation:
    """
    A structure representing a change in the state of the game board after an
    action has been played. Each mutation consists of a set of cell mutations.
    """
    action: Action
    cell_mutations: set[CellMutation]

    def __str__(self):
        return f"BoardMutation({self.cell_mutations})"


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
        initial_player: PlayerColor = PlayerColor.RED
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
        self._history: list[BoardMutation] = []

    def hash(self) -> tuple[tuple[CellState], PlayerColor]:
        return (tuple([coord[-1] for coord in sorted(self._state.items())]), self.turn_color)
    
    def get_legal_actions(self, player:PlayerColor|None=None) -> list[PlaceAction]:
        """
        Return the legal actions based on current state of board and player
        """
        
        # First action for red 
        if self.turn_count == 0: 
            return [
                PlaceAction(Coord(4,5), Coord(5,4), Coord(5,5), Coord(5,6)),
                PlaceAction(Coord(4,4), Coord(4,5), Coord(4,6), Coord(5,6)),
                PlaceAction(Coord(4,4), Coord(4,5), Coord(5,5), Coord(5,6)),
                PlaceAction(Coord(5,4), Coord(5,5), Coord(5,6), Coord(5,7)),
                PlaceAction(Coord(4,5), Coord(4,6), Coord(5,5), Coord(5,6))
            ]
        
        # First action for blue 
        elif self.turn_count == 1: 
            empty_coords = self._empty_coords()
            starting_cell = random.choice(list(empty_coords))
            action_coords = [starting_cell]
            visited_coords = {starting_cell}
            i = 0
            while i < 3:
                coord = action_coords[i]
                adj_coords = \
                    [coord.down(), coord.up(), coord.left(), coord.right()]
                empty_adj_coords = [coord for coord in adj_coords 
                                    if self._cell_empty(coord) and 
                                    coord not in visited_coords]
                next_coord = random.choice(empty_adj_coords)
                visited_coords.add(next_coord)
                action_coords.append(next_coord)
                i += 1
            return [PlaceAction(*action_coords)]
        
        # not the first action 
        else:
            legal_actions = set()
            visited_coords = set()

            if player == None: 
                player = self.turn_color

            for coord in self._player_occupied_coords(player):
                for adj_coord in [coord.down(), coord.up(), coord.left(), coord.right()]:
                    if not self._cell_empty(adj_coord) or adj_coord in visited_coords:
                        continue
                    visited_coords.add(adj_coord)
                    for piecetype in PieceType:
                        piece = _TEMPLATES[piecetype]
                        for rela_coord in piece:
                            real_piece = []
                            occupied = False
                            for real_coord in [adj_coord.__add__(target_rela_coord).__sub__(rela_coord) for target_rela_coord in piece]:
                                if not self._cell_empty(real_coord):
                                    occupied = True
                                    break
                                real_piece.append(real_coord)
                            if not occupied:
                                action = PlaceAction(real_piece[0], real_piece[1], real_piece[2], real_piece[3])
                                legal_actions.add(action)
        return list(legal_actions)
    
    # def get_legal_actions_at_cell(self, cell: Coord) -> list[PlaceAction]:
    #     """
    #     Return the legal tetromino placements with origina at the input cell
    #     """
    #     legal_actions = []
    #     for piecetype in PieceType:
    #         piece_coords = set(create_piece(piecetype, cell).coords)
    #         is_legal = all([self._cell_empty(coord) for coord in piece_coords])
    #         if is_legal:
    #             legal_actions.append(PlaceAction(*piece_coords))
    #     return legal_actions

    def __getitem__(self, cell: Coord) -> CellState:
        """
        Return the state of a cell on the board.
        """
        if not self._within_bounds(cell):
            raise IndexError(f"Cell position '{cell}' is invalid.")
        return self._state[cell]

    def apply_action(self, action: Action) -> BoardMutation:
        """
        Apply an action to a board, mutating the board state. Throws an
        IllegalActionException if the action is invalid.
        """
        match action:
            case PlaceAction():
                mutation = self._resolve_place_action(action)
            case _:
                raise IllegalActionException(
                    f"Unknown action {action}", self._turn_color)

        for cell_mutation in mutation.cell_mutations:
            self._state[cell_mutation.cell] = cell_mutation.next
        
        self._history.append(mutation)
        self._turn_color = self._turn_color.opponent

        return mutation

    def undo_action(self) -> BoardMutation:
        """
        Undo the last action played, mutating the board state. Throws an
        IndexError if no actions have been played.
        """
        if len(self._history) == 0:
            raise IndexError("No actions to undo.")

        mutation: BoardMutation = self._history.pop()

        self._turn_color = self._turn_color.opponent

        for cell_mutation in mutation.cell_mutations:
            self._state[cell_mutation.cell] = cell_mutation.prev

        return mutation

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
        return len(self._history)
    
    @property
    def turn_limit_reached(self) -> bool:
        """
        True iff the maximum number of turns has been reached.
        """
        return self.turn_count >= MAX_TURNS

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
        empty_coords = set(filter(self._cell_empty, self._state.keys()))

        if self.turn_limit_reached:
            return True

        # Try all possible piece types at all empty coordinates to see if there
        # are any legal moves remaining. This is quite inefficient, but good
        # enough for the referee's purposes.
        for piece_type in PieceType: 
            for coord in empty_coords:
                try:
                    piece_coords = set(create_piece(piece_type, coord).coords)

                    self.apply_action(PlaceAction(*piece_coords))
                    self.undo_action()

                    # If we got here, there's at least one legal move left.
                    return False
                
                except (ValueError, IllegalActionException):
                    pass

        # Tried all possible moves and none were legal.
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
        # print("coord:", coord, "colour:", self._state[coord])
        # try:
        #     print(self._state[coord].player == None)
        # except:
        #     print(self._state)
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
                f"Coord {coord} is already occupied with {self._state[coord].player}.", self._turn_color)
        
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

        if self.turn_count >= 2 and not has_neighbour:
            raise IllegalActionException(
                f"No coords in {action} neighbour a {self._turn_color} piece.",
                    self._turn_color)

        try:
            return Piece(action.coords)
        except ValueError as e:
            raise IllegalActionException(str(e), self._turn_color)

    def _resolve_place_action(self, action: PlaceAction) -> BoardMutation:
        piece = self._parse_place_action(action)
        coords_with_piece = self._occupied_coords() | set(piece.coords)

        min_r = min(c.r for c in piece.coords)
        max_r = max(c.r for c in piece.coords)
        min_c = min(c.c for c in piece.coords)
        max_c = max(c.c for c in piece.coords)
        
        # remove_r_coords = [
        #     Coord(r, c)
        #     for r in range(min_r, max_r + 1)
        #     for c in range(BOARD_N)
        #     if all(Coord(r, c) in coords_with_piece for c in range(BOARD_N))
        # ]

        # remove_c_coords = [
        #     Coord(r, c)
        #     for r in range(BOARD_N)
        #     for c in range(min_c, max_c + 1)
        #     if all(Coord(r, c) in coords_with_piece for r in range(BOARD_N))
        # ]

        remove_coords = []
        for r in range(min_r, max_r + 1): 
            if all(Coord(r, c) in coords_with_piece for c in range(BOARD_N)): 
                remove_coords += [Coord(r, c) for c in range(BOARD_N)]

        for c in range(min_c, max_c + 1): 
            if all(Coord(r, c) in coords_with_piece for r in range(BOARD_N)): 
                remove_coords += [Coord(r, c) for r in range(BOARD_N)]

        cell_mutations = {
            cell: CellMutation(
                cell, 
                self._state[cell], 
                CellState(self._turn_color)
            ) for cell in piece.coords
        }

        for cell in remove_coords: # remove_r_coords + remove_c_coords
            #print(f"remove cell {cell} for action {action}")
            cell_mutations[cell] = CellMutation(
                cell, 
                self._state[cell], 
                CellState(None)
            )

        return BoardMutation(
            action,
            cell_mutations=set(cell_mutations.values())
        )
