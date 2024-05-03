"""Games or Adversarial Search (Chapter 5)"""

import copy
import itertools
import random
from collections import namedtuple

import numpy as np

from .board import Board
from referee.game import PlayerColor

GameState = namedtuple('GameState', 'to_move, utility, board, moves')
StochasticGameState = namedtuple('StochasticGameState', 'to_move, utility, board, moves, chance')

# ______________________________________________________________________________

def alpha_beta_cutoff_search(board:Board):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player: PlayerColor = board._turn_color

    def cutoff_test(board:Board, depth, cutoff_depth=4):
        return depth > cutoff_depth or board.game_over()

    def eval_fn(board:Board) -> int: 
        if board.winner_color == player:
            return 1
        elif board.winner_color == player.opponent:
            return -1
        else:
            return 0

    # Functions used by alpha_beta
    def max_value(board:Board, alpha, beta, depth):
        if cutoff_test(board, depth):
            return eval_fn(board, player)
        v = -np.inf
        for a in board.get_legal_actions(): # TODO - the legal actions need to be ordered to increase the efficiency 
            board.apply_action(a) 
            v = max(v, min_value(board, alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
            board.undo_action()
        return v

    def min_value(board:Board, alpha, beta, depth):
        if cutoff_test(board, depth):
            return eval_fn(board, player)
        v = np.inf
        for a in board.get_legal_actions():
            board.apply_action(a)
            v = min(v, max_value(board, alpha, beta, depth + 1))
            if v <= alpha:
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






    

