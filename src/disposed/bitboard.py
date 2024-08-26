# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass

from referee.game.pieces import Piece, PieceType, create_piece, _TEMPLATES
from referee.game.coord import Coord, Direction
from referee.game.actions import Action, PlaceAction
from referee.game.constants import *

from utils.player import *

from collections import deque
from utils.constants import *
from disposed.boardstate import *
import random


class Game:
    """
    A class representing the game board for internal use in the referee. 
    """
    tetrominoes = {
    'I': ['1111'],
    'O': ['1100', '1100'],
    'T': ['111', '010'],
    'J': ['111', '001'],
    'L': ['111', '100'],
    'S': ['011', '110'],
    'Z': ['110', '011'],
    'I90': ['1', '1', '1', '1'],
    'O90': ['11', '11'],
    'T90': ['1', '11', '1'],
    'J90': ['1', '1', '11'],
    'L90': ['11', '1', '1'],
    'S90': ['10', '11', '01'],
    'Z90': ['01', '11', '10'],
    'I_FLIP': ['0001', '0001', '0001', '0001'],
    'O_FLIP': ['0011', '0011'],
    'T_FLIP': ['001', '011', '001'],
    'J_FLIP': ['001', '001', '011'],
    'L_FLIP': ['011', '001', '001']
    }

    def __init__(
        self, 
        initial_state: Board = None,
        initial_player: int = PlayerColor.RED
    ):
        """
        Create a new board. It is optionally possible to specify an initial
        board state (in practice this is only used for testing).
        """
        if initial_state is None:
            self._state = Board()
        else:
            self._state = initial_state
        self._turn_color: int = initial_player
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

    def apply_action(self, action: Action):
        """
        Apply an action to a board, mutating the board state.
        """
        self._resolve_place_action(action)
        self._turn_color = self._turn_color.opponent
        self._turn_count += 1
    
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
            red_count  = self._state._player_token_count(PlayerColor.RED)
            blue_count = self._state._player_token_count(PlayerColor.BLUE)
            balance    = red_count - blue_count

            if balance == 0:
                return None
            
            return PlayerColor.RED if balance > 0 else PlayerColor.BLUE

        else:
            # Current player cannot place any more pieces. Opponent wins.
            return self._turn_color.opponent

    def _resolve_place_action(self, action: PlaceAction):
        """
        Add piece to board and remove filled rows and columns.
        """
        row_nums = set(c.r for c in action.coords)
        col_nums = set(c.c for c in action.coords)
        coords_with_piece = self._occupied_coords() | set(action.coords)
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
            r = cell.r
            c = cell.c
            self._state.set_cell(r, c, None)
        
        for cell in action.coords:
            if cell not in remove_coords:
                r = cell.r
                c = cell.c
                self._state.set_cell(r, c, self._turn_color)