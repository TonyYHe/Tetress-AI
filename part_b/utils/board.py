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

@dataclass(frozen=True, slots=True)
class CellState:
    """
    A structure representing the state of a cell on the game board. A cell can
    be empty, or occupied by a player's token.
    """
    player: PlayerColor | None = None

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

class BoardState(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

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
        initial_state: BoardState = {},
        initial_player: PlayerColor = PlayerColor.RED,
    ):
        """
        Create a new board. It is optionally possible to specify an initial
        board state (in practice this is only used for testing).
        """
        if initial_state == {}:
            self._state: BoardState = BoardState({
                Coord(r, c): CellState() 
                for r in range(BOARD_N) 
                for c in range(BOARD_N)
            })
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
        if self._turn_count == 0 and self._turn_color == PlayerColor.RED:
            # there are only 5 distinct moves in an empty board due to the 
            # toroidal nature of the game board, and accounting for symmetry
            return [
                PlaceAction(Coord(4,5), Coord(5,4), Coord(5,5), Coord(5,6)),
                PlaceAction(Coord(4,4), Coord(4,5), Coord(4,6), Coord(5,6)),
                PlaceAction(Coord(4,4), Coord(4,5), Coord(5,5), Coord(5,6)),
                PlaceAction(Coord(5,4), Coord(5,5), Coord(5,6), Coord(5,7)),
                PlaceAction(Coord(4,5), Coord(4,6), Coord(5,5), Coord(5,6))
            ]
                
        elif self._turn_count == 1 and self._turn_color == PlayerColor.BLUE:
                return self.get_blue_first_action()
        # subsequent actions for each agent
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
                                real_piece.sort()
                                real_piece = PlaceAction(real_piece[0],
                                                         real_piece[1], 
                                                         real_piece[2], 
                                                         real_piece[3])
                                legal_actions.add(real_piece)
        return list(legal_actions)

    def get_blue_first_action(self):
        """
        Return a randomly generated action based on the chosen strategy.
        """
        def offensive_strategy():
            """
            Return placements adjacent to the only red piece on the board.
            """
            curr_turn_count = self._turn_count
            self.modify_turn_color()
            self._turn_count = 10
            legal_actions = self.get_legal_actions()
            self.modify_turn_color()
            self._turn_count = curr_turn_count
            return legal_actions
        
        def random_strategy(starting_cell):
            """
            Return a completely random move.
            """
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
        
        def defensive_strategy():
            """
            Return a random placement far away from the only red piece on the 
            board.
            """
            red_coords = self._occupied_coords()
            row_nums = [coord.r for coord in red_coords]
            col_nums = [coord.r for coord in red_coords]
            max_r = max(row_nums)
            max_c = max(col_nums)
            sc_r = (max_r + 5 + BOARD_N) % BOARD_N
            sc_c = (max_c + 5 + BOARD_N) % BOARD_N
            starting_cell = Coord(sc_r, sc_c)
            return random_strategy(starting_cell)
        empty_coords = self._empty_coords()
        starting_cell = random.choice(list(empty_coords))
        return random_strategy(starting_cell)

    def __getitem__(self, cell: Coord) -> CellState:
        """
        Return the state of a cell on the board.
        """
        if not self._within_bounds(cell):
            raise IndexError(f"Cell position '{cell}' is invalid.")
        return self._state[cell]

    def apply_action(self, action: Action) -> BoardMutation:
        """
        Apply an action to a board, mutating the board state.
        """
        board_mutation = self._resolve_place_action(action)
        self._turn_color = self._turn_color.opponent
        self._turn_count += 1
        return board_mutation

    
    def undo_action(self, board_mutation: BoardMutation) -> BoardMutation:
        """
        Undo the last action played, mutating the board state. Throws an
        IndexError if no actions have been played.
        """
        self._turn_color = self._turn_color.opponent
        self._turn_count -= 1

        for cell_mutation in board_mutation.cell_mutations:
            self._state[cell_mutation.cell] = cell_mutation.prev

        return board_mutation

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

    def modify_turn_color(self, color: PlayerColor = None) -> PlayerColor:
        if color is None:
            self._turn_color = self._turn_color.opponent
        else:
            self._turn_color = color
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
        
        # find clusters of empty cells using BFS
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
        
        # check if clusters of size >= 4 has neighbouring red/blue cells, if so
        # then a piece can be placed in this cluster
        for _, [coords, length] in empty_coord_clusters.items():
            if length < 4:
                continue
            for coord in coords:
                if self._has_neighbour(coord, self._turn_color):
                    return False
    
        return True
    
    def game_result(self, player_color: PlayerColor):
        """Returns the utility value of the terminal node."""
        if self.winner_color == player_color:
            return WIN
        elif self.winner_color == player_color.opponent:
            return LOSS
        else:
            return DRAW
        
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

    def _resolve_place_action(self, action: PlaceAction):
        """
        Add piece to board and remove filled rows and columns.
        """
        row_nums = set(c.r for c in action.coords)
        col_nums = set(c.c for c in action.coords)
        coords_with_piece = self._occupied_coords() | set(action.coords)
        cell_mutations = dict()
        remove_coords = set()

        # scan all the coordinates in the same row as the input piece (action)
        for r in row_nums:
            remove_r_coords = []
            filled = True
            for c in range(BOARD_N):
                cell = Coord(r, c)
                if cell not in coords_with_piece:
                    filled = False
                    break
                remove_r_coords.append(cell)
            if not filled:
                continue
            remove_coords.update(remove_r_coords)
        
        # scan all the coordinates in the same col as the input piece (action)
        for c in col_nums:
            remove_c_coords = []
            filled = True
            for r in range(BOARD_N):
                cell = Coord(r, c)
                if cell not in coords_with_piece:
                    filled = False
                    break
                remove_c_coords.append(cell)
            if not filled:
                continue
            remove_coords.update(remove_c_coords)
            
        for cell in remove_coords:
            cell_mutations[cell] = CellMutation(cell, self._state[cell], CellState(None))
            self._state[cell] = CellState(None)
        
        for cell in action.coords:
            if cell not in remove_coords:
                cell_mutations[cell] = CellMutation(cell, self._state[cell], CellState(self._turn_color))
                self._state[cell] = CellState(self._turn_color)

        return BoardMutation(
            action,
            cell_mutations=set(cell_mutations.values())
        )
    
    def eval_fn(self, player_color: PlayerColor, ply: int):
        """
        problematic
        Return a utility value calculated from the persepctive of the input 
        player, given a board. The input player color should always be THE 
        PLAYER (YOU).
        """
        if self.winner_color is not None:
            if self.winner_color == player_color:
                return 1000 - ply
            else:
                return -1000 + ply
            
        # Find the difference in the number of actions 
        extra_num_actions = self.diff_legal_actions()
        # extra_num_reachable = self.diff_reachable_valid_empty_cell()
        extra_num_occupied = self.diff_cells_occupied()

        if self._turn_count <= TURN_THRESHOLD:
            utility = extra_num_actions + extra_num_occupied*0.1
        else:
            turns_exceed_threshold = self.turn_count - TURN_THRESHOLD
            utility = extra_num_actions + extra_num_occupied*turns_exceed_threshold*0.5

        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if player_color == self._turn_color else -utility
    
    
    def diff_cells_occupied(self) -> int:
        """
        Find the difference in the number of tokens between the player and the 
        opponent. 
        """
        return self._player_token_count(self._turn_color) - self._player_token_count(self._turn_color.opponent)

    def diff_legal_actions(self) -> int: 
        """
        Find the difference in the number of legal actions between the player and 
        the opponent. 
        """
        curr_color = self._turn_color
        num_player_legal_actions = len(self.get_legal_actions())
        self._turn_color = curr_color.opponent
        num_opponent_legal_actions = len(self.get_legal_actions())
        self._turn_color = curr_color
        return num_player_legal_actions - num_opponent_legal_actions
    
    # def diff_reachable_valid_empty_cell(self) -> int: 
    #     ''' Find the difference in the number of valid empty cells reachable 
    #         between the player and the opponent. 
    #         A cell is valid if it is connected to at least 3 other empty cells. 
    #     '''
    #     return self.num_empty_player_reachable - self.num_empty_opponent_reachable
    
    # def empty_connected(self, board: Board, empty: Coord) -> set[Coord]:
    #     ''' Return the empty cells connected to the `empty` cell
    #     '''
    #     frontier = [empty]
    #     connected = {empty}
    #     while frontier: 
    #         visiting = frontier.pop()
    #         for adjacent in [visiting.__add__(direction) for direction in Direction]: 
    #             if board._cell_empty(adjacent) and adjacent not in connected: 
    #                 frontier.append(adjacent)
    #                 connected.add(adjacent)
    #     return connected
    
    # def num_valid_reachable_cells(self, board:Board, player:PlayerColor) -> int: 
    #     reachable = 0
    #     visited = set()
    #     occupied = board._player_occupied_coords(player)
    #     for cell in occupied: 
    #         for adjacent in [cell.__add__(direction) for direction in Direction]: 
    #             if board._cell_empty(adjacent) and adjacent not in visited: 
    #                 connected = self.empty_connected(board, adjacent)
    #                 # _testing.show(connected, description="new empty region connected")
    #                 # _testing.show(visited, description="previously visited empty region")
    #                 assert(len(visited.intersection(connected)) == 0)  # `connected` should be a new region that has not been visited 
    #                 visited.update(connected)
                    
    #                 # Only add valid cell count to the output 
    #                 if len(connected) >= 4: 
    #                     reachable += len(connected)
    #     return reachable