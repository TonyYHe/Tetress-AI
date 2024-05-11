from referee.game.coord import Coord, Direction
from referee.game.player import PlayerColor
from referee.game.actions import Action, PlaceAction
from referee.game.constants import *

from utils.board import Board
import copy
from collections import deque

from referee.game.constants import MAX_TURNS
TURN_THRESHOLD = MAX_TURNS * 0.8 

def eval_fn(board: Board, player_color: PlayerColor, 
            transposition_table: dict, game_over=False):
        """
        This is problematic.
        Return a positive utility value for the player, and a negative utility 
        value for the opponent.
        """
        if game_over == True:
            return board.game_result() * 1000
        
        boardstate = board._state
        curr_color = board._turn_color

        # check if the utility of the current state has been calculated already
        utility = transposition_table.get(boardstate)
        if utility is not None:
            return utility

        # Find the difference in the number of actions 
        extra_num_actions = diff_legal_actions(board, player_color)
        # Find the difference in the number of empty cells reachable that can be used as an action 
        extra_num_reachable = diff_reachable_valid_empty_cell(board, player_color)
        # Find the difference in the number of cells occupied 
        extra_num_occupied = diff_cells_occupied(board, player_color)

         # it's best to normalise this result to [-1, 1]
        if board._turn_count < TURN_THRESHOLD: 
            # Far away from turns limitation 
            utility = (
                extra_num_actions +         \
                extra_num_reachable +       \
                extra_num_occupied * 0.1 
            )
        else: 
            # If about to reach turns limit, evalution also include the number of cells occupied 
            turns_exceed_threshold = board._turn_count - TURN_THRESHOLD
            utility = (
                extra_num_actions +                                 \
                extra_num_reachable +                               \
                extra_num_occupied * turns_exceed_threshold * 0.5 
            )
        transposition_table[board] = utility
        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if player_color == curr_color else -utility


def action_utility(board: Board, action: PlaceAction, player: PlayerColor) -> int: 
    '''Find the utility of an action for sorting the action for maximize pruning 
    '''

    new_board = copy.deepcopy(board)
    new_board.apply_action(action)

    # Calculate the weighted sum of the utility components for `player` (i.e. the agent using the habp) 
    utility = (
        diff_row_col_occupied(new_board, player) * 0.8 +    \
        #diff_cells_occupied(new_board, player) * 0.5 +      \
        diff_reachable_valid_empty_cell(new_board, player)
    )
    return utility


# =============== Utility Evaluation Fundctions ==================== 

def diff_cells_occupied(board: Board, player: PlayerColor) -> int:
    """
    Find the difference in the number of tokens between the player and the 
    opponent. 
    """
    num_player_occupied = board._player_token_count(player)
    num_opponent_occupied = board._player_token_count(player.opponent)
    return num_player_occupied - num_opponent_occupied


def diff_legal_actions(board: Board, player: PlayerColor) -> int: 
    """
    Find the difference in the number of legal actions between the player and 
    the opponent. 
    """
    curr_color = board._turn_color
    board.modify_turn_color(player)
    num_player_actions = len(board.get_legal_actions())
    board.modify_turn_color(player.opponent)
    num_opponent_actions = len(board.get_legal_actions())
    board.modify_turn_color(curr_color)
    return num_player_actions - num_opponent_actions

# def diff_reachable_valid_empty_cells(board: Board, player: PlayerColor) -> int:
#     """
#     Return the difference in the number of valid empty cells reachable between the 
#     player and the opponent. A cell is valid if it is connected to at least 3 
#     other empty cells. 
#     """
#     def num_reachable_valid_empty_cells(board: Board, player: PlayerColor):
#         """
#         Return the number number of valid empty cells reachable by the player.
#         A cell is validly reachable if it is connected to at least 3 other empty cells. 

#         """
#         visited = set()
#         player_occupied_cells = [(coord, 0) for coord in board._player_occupied_coords(player)]
#         frontier = deque(player_occupied_cells)
#         while frontier:
#             item = frontier.popleft()
#             coord = item[0]
#             dist_to_closest_token = item[1]
#             visited.add(coord)
#             if dist_to_closest_token >= 4:
#                 continue
#             adj_coords = [coord.down(), coord.up(), coord.left(), coord.right()]
#             empty_unvisited_adj_coords = [
#                 adj_coord for adj_coord in adj_coords 
#                 if board._cell_empty(adj_coord) and adj_coord not in visited
#                 ]
#             for adj_coord in empty_unvisited_adj_coords:
#                 frontier.append((adj_coord, dist_to_closest_token + 1))
#         return len(visited) - len(player_occupied_cells)
#     num_empty_player_reachable = num_reachable_valid_empty_cells(board, player)
#     num_empty_opponent_reachable = num_reachable_valid_empty_cells(board, player.opponent)
#     return num_empty_player_reachable - num_empty_opponent_reachable
    


def diff_reachable_valid_empty_cell(board:Board, player:PlayerColor) -> int: 
    """
    Find the difference in the number of valid empty cells reachable between the 
    player and the opponent. A cell is valid if it is connected to at least 3 
    other empty cells. 
    """
    def empty_connected(board:Board, empty:Coord) -> set[Coord]:
        """
        Return the empty cells connected to the `empty` cell
        """
        frontier = [empty]
        connected = {empty}
        while frontier: 
            visiting = frontier.pop()
            for adjacent in [visiting.__add__(direction) for direction in Direction]: 
                if board._cell_empty(adjacent) and adjacent not in connected: 
                    frontier.append(adjacent)
                    connected.add(adjacent)
        return connected
    
    def num_valid_reachable_cells(board:Board, player:PlayerColor) -> int: 
        reachable = 0
        visited = set()
        occupied = board._player_occupied_coords(player)
        for cell in occupied: 
            for adjacent in [cell.__add__(direction) for direction in Direction]: 
                if board._cell_empty(adjacent) and adjacent not in visited: 
                    connected = empty_connected(board, adjacent)
                    # _testing.show(connected, description="new empty region connected")
                    # _testing.show(visited, description="previously visited empty region")
                    assert(len(visited.intersection(connected)) == 0)  # `connected` should be a new region that has not been visited 
                    visited.update(connected)
                    
                    # Only add valid cell count to the output 
                    if len(connected) >= 4: 
                        reachable += len(connected)
        return reachable
    
    num_empty_player_reachable = num_valid_reachable_cells(board, player)
    num_empty_opponent_reachable = num_valid_reachable_cells(board, player.opponent)
    return num_empty_player_reachable - num_empty_opponent_reachable


def diff_row_col_occupied(board:Board, player:PlayerColor) -> int: 
    """
    Find the difference in the sum of the number of rows and columns occupied 
    between the player and the opponent. 
    """
    player_occupied = (board._player_occupied_coords(player)) 
    opponent_occupied = (board._player_occupied_coords(player.opponent)) 
    player_occupied_row = set(map(lambda coord: coord.r, player_occupied))
    player_occupied_col = set(map(lambda coord: coord.c, player_occupied))
    opponent_occupied_row = set(map(lambda coord: coord.r, opponent_occupied))
    opponent_occupied_col = set(map(lambda coord: coord.c, opponent_occupied))
    return len(player_occupied_row) + len(player_occupied_col) \
        - len(opponent_occupied_row) - len(opponent_occupied_col)