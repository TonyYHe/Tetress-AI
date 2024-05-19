"""Games or Adversarial Search (Chapter 5)"""

import copy
import itertools
import random
from collections import namedtuple

import numpy as np
import time

from .board import Board, BOARD_N, Direction, Coord, CellState
from referee.game import PlaceAction, PlayerColor
from referee.agent.resources import CountdownTimer
from . import _testing
from referee.run import game_delay

# ______________________________________________________________________________

# For testing  
def _print(*values): 
    ''' Change this function name to `_print` if want to print out debug messages '''
    pass 

# ______________________________________________________________________________


MAX_TURN = 150 
TURN_THRESHOLD = MAX_TURN * 0.8 
MIN_ACTIONS_TEST = 20
TIME_OUT_FACTOR = 30

class Entry: 
    def __init__(self, utility:float|None=None, actions:list[PlaceAction]=[]): 
        ''' Initialize a node; `player` should be the colour of the agent
        '''
        #self.board: Board = board 
        self.utility: float = utility
        self.topK_actions:list[PlaceAction] = actions
    

class TranspositionTable: 
    def __init__(self, player:PlayerColor): 
        '''Each player uses its own transposition table where the utility is in the perspective of the player. 
        '''
        self.player = player 

        # key = board state, (include the state of the board, the turn color, and the turn count if exceed the threshold)
        # value = node  
        self.transposition_table: dict[tuple[PlayerColor|None], Entry] = {} 
    

    def get_entry(self, board:Board): 
        # The key need to include the specific turn count for turns greater than the threshold, since the utility can be different
        state_key:tuple[tuple[tuple[CellState], PlayerColor], int] = (board.hash(), max(TURN_THRESHOLD, board.turn_count))

        # Create new entry if key does not previously exist in the table 
        if not self.transposition_table.get(state_key): 
            self.transposition_table[state_key] = Entry(utility=eval_fn(board, self.player))
        return self.transposition_table[state_key]


    def get_utility(self, board:Board): 
        state_key:tuple[tuple[tuple[CellState], PlayerColor], int] = (board.hash(), max(TURN_THRESHOLD, board.turn_count))
        if self.transposition_table.get(state_key): 
            print(_testing.prefix(10), "------ revisiting utility")
        entry = self.get_entry(board)
        return entry.utility
    

    def get_topK_actions(self, board:Board, K:int=15):
        entry = self.get_entry(board)
        if not entry.topK_actions:
            def eval(action:PlaceAction) -> float: 
                board.apply_action(action) 
                utility = eval_fn_ordering(board, self.player)
                board.undo_action()
                return utility
            entry.topK_actions = sorted(board.get_legal_actions(), key=lambda action: eval(action), reverse=(board.turn_color==self.player))[:K]
        else: 
            print(f"----- revisit the top k children")
        return entry.topK_actions
        

def alpha_beta_cutoff_search(board:Board, transposition_table:TranspositionTable, referee):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    player = board.turn_color
    deepest = 1

    def cutoff_test(board:Board, depth):
        # If the board is relatively empty, simply check until a certain depth  
        if board.game_over: 
            return True
        
        # if len(board._empty_coords()) > BOARD_N * BOARD_N / 3: 
        #     return depth > 2
        # if len(board._empty_coords()) > BOARD_N * BOARD_N / 4:
        #     return depth > 3

        # TODO - if the state of the game is unstable, go deeper? 
        # if not board.is_stable(): 
        #     return depth > 5
        # else: 
        return depth > deepest

    # Functions used by alpha_beta
    def max_value(board:Board, alpha, beta, depth) -> float:
        if cutoff_test(board, depth):
            return transposition_table.get_utility(board)
        v = -np.inf
        top_actions = transposition_table.get_topK_actions(board)
        _search = 0
        for action in top_actions: 
            print(_testing.prefix(27), f"max-val apply action {action} in max_value() with depth {depth}")
            board.apply_action(action)
            v = max(v, min_value(board, alpha, beta, depth + 1))
            board.undo_action()
            _search += 1
            if v >= beta:
                print(_testing.prefix(10), f"pruned {15-_search} nodes at depth {depth}, exceed the maximum")
                return v
            alpha = max(alpha, v)
        return v

    def min_value(board:Board, alpha, beta, depth) -> float:
        if cutoff_test(board, depth):
            return transposition_table.get_utility(board)
        v = np.inf
        top_actions = transposition_table.get_topK_actions(board)
        _search = 0
        for action in top_actions:
            print(_testing.prefix(27), f"min-val apply action {action} in max_value() with depth {depth}")
            board.apply_action(action)
            v = min(v, max_value(board, alpha, beta, depth + 1))
            board.undo_action()
            _search += 1
            if v <= alpha:
                print(_testing.prefix(10), f"pruned {15-_search} nodes at depth {depth}, exceed the minimum")
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_cutoff_search starts here:
    best_score = -np.inf
    beta = np.inf
    best_action = None

    legal_actions = board.get_legal_actions()
    print(_testing.prefix(17), f"number of legal actions = {len(legal_actions)}")

    # if len(legal_actions) < MIN_ACTIONS_TEST: 
    #     random_index = range(len(legal_actions))
    # else: 
    #     random_index:set[int] = set([random.randint(0, len(legal_actions)-1) for _ in range(MIN_ACTIONS_TEST)])
    # print(_testing.prefix(17), random_index) 

    top_actions = transposition_table.get_topK_actions(board)
    start_time = time.time()
    base_time = referee["time_remaining"] / (MAX_TURN - board.turn_count)
    end_time = start_time + base_time + board.turn_count/TIME_OUT_FACTOR
    while (time.time() < end_time and deepest < 30):
        for action in top_actions: #[legal_actions[i] for i in random_index]
            # timer = CountdownTimer(time_limit=1,tolerance=10)
            # timer.__enter__()

            # Apply the action, evaluate alpha and beta, then undo the action 
            board.apply_action(action)     
            v = min_value(board, best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_action = action
            board.undo_action()
            # timer.__exit__(None, None, None)
        deepest += 1
    print(_testing.prefix(5), f"reach deepest at {deepest} at a testing turn count {board.turn_count}")
    return best_action


def eval_fn_ordering(board:Board, player:PlayerColor) -> int: 
    ''' Find the utility of an action for sorting the action for maximize pruning. 
    '''

    # Calculate the weighted sum of the utility components for `player` (i.e. the agent using the habp) 
    if (board.turn_count < 20):
        utility = (
            diff_row_col_occupied(board, player) +    \
            #diff_cells_occupied(new_board, player) * 0.5 +      \
            diff_reachable_valid_empty_cell(board, player) 
        )
    else: 
        utility = (
            diff_row_col_occupied(board, player) * 0.5 +    \
            diff_reachable_valid_empty_cell(board, player)
        )

    return utility


def eval_fn(board:Board, player:PlayerColor) -> float: 
    ''' Find the utility of terminal state. 
    '''
    print(_testing.prefix(), f"evaluate start for player {player}")
    # If there is a winner, give the result straight away 
    if board.winner_color == player.opponent: 
        return -1000
    elif board.winner_color == player: 
        return 1000 - board.turn_count

    # Otherwise, evaluate the game state 

    # Find the difference in the number of actions 
    extra_num_actions = diff_legal_actions(board, player)

    # Find the difference in the number of empty cells reachable that can be used as an action 
    extra_num_reachable = diff_reachable_valid_empty_cell(board, player)

    # Find the difference in the number of cells occupied 
    extra_num_occupied = diff_cells_occupied(board, player)

    if board.turn_count <= TURN_THRESHOLD: 
        # Far away from turns limitation 
        utility = (
            extra_num_actions +         \
            extra_num_reachable +       \
            extra_num_occupied * 0.1 
        )
    else: 
        # If about to reach turns limit, evalution also include the number of cells occupied 
        turns_exceed_threshold = board.turn_count - TURN_THRESHOLD
        utility = (
            extra_num_actions +                                 \
            extra_num_reachable +                               \
            extra_num_occupied * turns_exceed_threshold * 0.5 
        )
    
    print(_testing.prefix(), f"evaluate end, utility={utility}")
    return utility


# =============== Utility Evaluation Fundctions ==================== 

def diff_cells_occupied(board:Board, player:PlayerColor) -> int:
    num_player_occupied = board._player_token_count(player)
    num_opponent_occupied = board._player_token_count(player.opponent)
    return num_player_occupied - num_opponent_occupied


def diff_legal_actions(board:Board, player:PlayerColor) -> int: 
    ''' Find the difference in the number of legal actions 
        between the player and the opponent. 
    '''
    num_actions = len(board.get_legal_actions(player))
    num_opponent_actions = len(board.get_legal_actions(player.opponent))
    return num_actions - num_opponent_actions


def diff_reachable_valid_empty_cell(board:Board, player:PlayerColor) -> int: 
    ''' Find the difference in the number of valid empty cells reachable 
        between the player and the opponent. 
        A cell is valid if it is connected to at least 3 other empty cells. 
    '''
    def empty_connected(board:Board, empty:Coord) -> set[Coord]:
        ''' Return the empty cells connected to the `empty` cell
        '''
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
    ''' Find the difference in the sum of the number of rows and columns occupied
        between the player and the opponent. 
    '''
    player_occupied = (board._player_occupied_coords(player)) 
    opponent_occupied = (board._player_occupied_coords(player.opponent)) 
    player_occupied_row = set(map(lambda coord: coord.r, player_occupied))
    player_occupied_col = set(map(lambda coord: coord.c, player_occupied))
    opponent_occupied_row = set(map(lambda coord: coord.r, opponent_occupied))
    opponent_occupied_col = set(map(lambda coord: coord.c, opponent_occupied))
    return len(player_occupied_row) + len(player_occupied_col) \
        - len(opponent_occupied_row) - len(opponent_occupied_col)


# ______________________________________________________________________________
# Players for Games

def query_player(game, state):
    """Make a move by querying standard input."""
    print("current state:")
    game.display(state)
    print("available moves: {}".format(game.actions(state)))
    print("")
    move = None
    if game.actions(state):
        move_string = input('Your move? ')
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    else:
        print('no legal moves: passing turn to next player')
    return move


def alpha_beta_player(game, state):
    return alpha_beta_cutoff_search(state, game)







    

