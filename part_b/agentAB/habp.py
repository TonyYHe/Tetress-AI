"""Games or Adversarial Search (Chapter 5)"""

import copy
import itertools
import random
from collections import namedtuple

import numpy as np

from .board import Board, BOARD_N, Direction, Coord, CellState
from referee.game import PlaceAction, PlayerColor
from referee.agent.resources import CountdownTimer
from . import _testing
from referee.run import game_delay

GameState = namedtuple('GameState', 'to_move, utility, board, moves')
StochasticGameState = namedtuple('StochasticGameState', 'to_move, utility, board, moves, chance')

# ______________________________________________________________________________

MAX_TURN = 150 
TURN_THRESHOLD = MAX_TURN * 0.8 

def print(*values): 
    ''' Change this function name to `_print` if want to print out debug messages '''
    pass 

def alpha_beta_cutoff_search(board:Board):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    player = board.turn_color

    def cutoff_test(board:Board, depth):
        # If the board is relatively empty, simply check until a certain depth  
        SPARSE_THREASHOLD = BOARD_N * BOARD_N / 3
        if len(board._empty_coords()) > SPARSE_THREASHOLD: 
            return depth > 2

        # TODO - if the state of the game is unstable, go deeper? 
        # if not board.is_stable(): 
        #     return depth > 5
        # else: 
        return depth > 4 or board.game_over

    def eval_fn(board:Board, player:PlayerColor) -> float: 
        print(_testing.prefix(), "evaluate start")
        # If there is a winner, give the result straight away 
        if board.winner_color == player.opponent: 
            return -1 
        elif board.winner_color == player: 
            return 1,000,000,000,000

        # Otherwise, evaluate the game state 

        # Find the difference in the number of actions 
        # num_actions = len(board.get_legal_actions(player))
        # num_opponent_actions = len(board.get_legal_actions(player.opponent))
        # extra_num_actions = num_actions - num_opponent_actions

        # Find the difference in the number of empty cells reachable that can be used as an action 
        extra_num_reachable = diff_reachable_valid_empty_cell(board, player)

        # Find the difference in the number of cells occupied 
        extra_num_occupied = diff_cells_occupied(board, player)

        if board.turn_count < TURN_THRESHOLD: 
            utility = extra_num_reachable + 0.1 * extra_num_occupied
        else: 
            # If about to reach turns limit, evalution also include the number of cells occupied 
            utility = extra_num_reachable + \
                (board.turn_count - TURN_THRESHOLD) * 0.5 * extra_num_occupied
        
        print(_testing.prefix(), "evaluate end")
        return utility

    # Functions used by alpha_beta
    def max_value(board:Board, alpha, beta, depth) -> float:
        if cutoff_test(board, depth):
            return eval_fn(board, player)
        v = -np.inf
        #for a in board.get_legal_actions():
        for action in sorted(board.get_legal_actions(), key=lambda action: action_utility(board, action, player), reverse=True)[:10]: 
            print(_testing.prefix(27), f"max-val apply action {action} in max_value() with depth {depth}")
            new_board = copy.deepcopy(board)
            new_board.apply_action(action)
            v = max(v, min_value(new_board, alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(board:Board, alpha, beta, depth) -> float:
        if cutoff_test(board, depth):
            return eval_fn(board, player)
        v = np.inf
        # for a in board.get_legal_actions():
        for action in sorted(board.get_legal_actions(), key=lambda action: action_utility(board, action, player))[:10]:
            print(_testing.prefix(27), f"min-val apply action {action} in max_value() with depth {depth}")
            new_board = copy.deepcopy(board)
            new_board.apply_action(action)
            v = min(v, max_value(board, alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_cutoff_search starts here:
    best_score = -np.inf
    beta = np.inf
    best_action = None

    legal_actions = board.get_legal_actions()
    print(_testing.prefix(17), f"number of legal actions = {len(legal_actions)}")

    MIN_ACTIONS_TEST = 30
    if len(legal_actions) < MIN_ACTIONS_TEST: 
        random_index = range(len(legal_actions))
    else: 
        random_index:set[int] = set([random.randint(0, len(legal_actions)-1) for _ in range(MIN_ACTIONS_TEST)])
    print(_testing.prefix(17), random_index) 

    for action in [legal_actions[i] for i in random_index]:
        game_delay(1000)
        # timer = CountdownTimer(time_limit=1,tolerance=10)
        # timer.__enter__()

        # Apply the action, evaluate alpha and beta, then undo the action 
        new_board = copy.deepcopy(board)   
        new_board.apply_action(action)     
        v = min_value(new_board, best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = action

        # timer.__exit__(None, None, None)
    return best_action


def action_utility(board:Board, action:PlaceAction, player:PlayerColor) -> int: 
    '''Find the utility of an action for sorting the action for maximize pruning 
    '''

    new_board = copy.deepcopy(board)
    new_board.apply_action(action)

    # Calculate the weighted sum of the utility components for `player` (i.e. the agent using the habp) of the new action played 
    utility = diff_row_col_occupied(new_board, player) # TODO - add more component to make the weighted sum more accurate 
    return utility


# =============== Utility Evaluation Fundctions ==================== 

def diff_cells_occupied(board:Board, player:PlayerColor) -> int:
    num_player_occupied = board._player_token_count(player)
    num_opponent_occupied = board._player_token_count(player.opponent)
    return num_player_occupied - num_opponent_occupied


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


# ______________________________________________________________________________
# Some Sample Games


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))



    

