"""Games or Adversarial Search (Chapter 5)"""

import copy
import itertools
import random
from collections import namedtuple

import numpy as np

from .board import Board, BOARD_N
from referee.game import PlaceAction, PlayerColor
from referee.agent.resources import CountdownTimer

GameState = namedtuple('GameState', 'to_move, utility, board, moves')
StochasticGameState = namedtuple('StochasticGameState', 'to_move, utility, board, moves, chance')

# ______________________________________________________________________________

MAX_TURN = 150 
TURN_THRESHOLD = MAX_TURN * 0.8 

def action_utility(board:Board, action:PlaceAction) -> int: 
    '''Find the utility of an action for sorting the action for maximize pruning 
    '''
    board.apply_action(action) 
    player_occupied = (board._player_occupied_coords(board.turn_color.opponent)) # the colour of the action
    opponent_occupied = (board._player_occupied_coords(board.turn_color)) # the opponent colour of the action 
    board.undo_action()

    player_occupied_row = set(map(lambda coord: coord.r, player_occupied))
    player_occupied_col = set(map(lambda coord: coord.c, player_occupied))
    opponent_occupied_row = set(map(lambda coord: coord.r, opponent_occupied))
    opponent_occupied_col = set(map(lambda coord: coord.c, opponent_occupied))

    return len(player_occupied_row) + len(player_occupied_col) - len(opponent_occupied_row) - len(opponent_occupied_col)


def alpha_beta_cutoff_search(board:Board):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    player = board.turn_color

    def cutoff_test(board:Board, depth):
        # If the board is relatively empty, simply check until a certain depth  
        SPARSE_THREASHOLD = BOARD_N * BOARD_N / 3
        if len(board._empty_coords()) > SPARSE_THREASHOLD: 
            return depth > 1

        # TODO - if the state of the game is unstable, go deeper? 
        # if board.is_stable(): 
        #     return depth > 5
        # else: 
        return depth > 4 or board.game_over

    def eval_fn(board:Board, player:PlayerColor) -> int: 
        timer = CountdownTimer(time_limit=2)
        timer.__enter__()

        # If there is a winner, give the result straight away 
        if board.winner_color == player.opponent: 
            return -1 
        elif board.winner_color == player: 
            return 1,000,000,000,000

        # Otherwise, evaluate the game state 
        num_actions = len(board.get_legal_actions(player))
        player_occupied = board._player_occupied_coords(player)
        opponent_occupied = board._player_occupied_coords(player.opponent)
        extra_num_occupied = len(player_occupied) - len(opponent_occupied)
        if board.turn_count < TURN_THRESHOLD: 
            utility = num_actions + 0.1 * extra_num_occupied
        else: 
            # If about to reach turns limit, evalution also include the number of cells occupied 
            utility = num_actions + \
                (board.turn_count - TURN_THRESHOLD) * 0.5 * extra_num_occupied
        
        timer.__exit__(None, None, None)
        return utility

    def _action_utility(board, action) -> int: 
        print("action_utility")
        timer = CountdownTimer(time_limit=2)
        timer.__enter__()
        board.apply_action(action) 
        utility = eval_fn(board)
        board.undo_action()
        timer.__exit__(None, None, None)
        return utility 

    # Functions used by alpha_beta
    def max_value(board:Board, alpha, beta, depth):
        if cutoff_test(board, depth):
            return eval_fn(board, player)
        v = -np.inf
        #for a in board.get_legal_actions():
        for a in sorted(board.get_legal_actions(), key=lambda action: action_utility(board, action), reverse=True): 
            #print(f"apply action {a} in max_value() with depth {depth}")
            board.apply_action(a) 
            v = max(v, min_value(board, alpha, beta, depth + 1))
            if v >= beta:
                board.undo_action()
                return v
            alpha = max(alpha, v)
            board.undo_action()
        return v

    def min_value(board:Board, alpha, beta, depth):
        if cutoff_test(board, depth):
            return eval_fn(board, player)
        v = np.inf
        # for a in board.get_legal_actions():
        for a in sorted(board.get_legal_actions(), key=lambda action: action_utility(board, action), reverse=True):
            #print(f"apply action {a} in min_value() with depth {depth}")
            board.apply_action(a)
            v = min(v, max_value(board, alpha, beta, depth + 1))
            if v <= alpha:
                board.undo_action()
                return v
            beta = min(beta, v)
            board.undo_action()
        return v

    # Body of alpha_beta_cutoff_search starts here:
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in board.get_legal_actions():
        board.apply_action(a)
        v = min_value(board, best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
        board.undo_action()
    return best_action


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






    

