import numpy as np

from agent.board import Board
from copy import deepcopy

# ______________________________________________________________________________
class HABPNode():
    def __init__(self, board: Board, color, parent=None, parent_action=None):
        self.state = board
        self.color = color
        self.parent = parent
        self.parent_action = parent_action
        self.children = dict()
        return
    
    def alpha_beta_cutoff_search(self):
        """Search game to determine best action; use alpha-beta pruning.
        This version cuts off search and uses an evaluation function."""

        # Body of alpha_beta_cutoff_search starts here:
        # The default test cuts off at depth d or at a terminal state
        best_score = -np.inf
        beta = np.inf
        best_child = None
        for a in self.state.get_legal_actions():
            new_board = deepcopy(self.state)
            new_board.apply_action(a)
            child_node = HABPNode(new_board, self.color, self, a)
            self.children[a] = child_node
            v = child_node.min_value(best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_child = a
        return best_child
    
    # Functions used by alpha_beta
    def max_value(self, alpha, beta, depth):
        print("max, alpha:", alpha, "beta:", beta, "depth:", depth)
        if self.cutoff_test(depth):
            return self.eval_fn()
        v = -np.inf
        for a in self.state.get_legal_actions():
            new_board = deepcopy(self.state)
            new_board.apply_action(a)
            child_node = HABPNode(new_board, self.color, self, a)
            self.children[a] = child_node
            v = max(v, child_node.min_value(alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, alpha, beta, depth):
        print("min, alpha:", alpha, "beta:", beta, "depth:", depth)
        if self.cutoff_test(depth):
            return self.eval_fn()
        v = np.inf
        for a in self.state.get_legal_actions():
            new_board = deepcopy(self.state)
            new_board.apply_action(a)
            child_node = HABPNode(new_board, self.color, self, a)
            self.children[a] = child_node
            v = min(v, child_node.max_value(alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v        
    
    def cutoff_test(self, depth):
        d = 4
        return depth > d or self.state.game_over
    
    def eval_fn(self):
        """
        This is problematic.
        """
        board = self.state
        player_color = board._turn_color

        # calculate how many more legal actions can the player take compared
        # to the opponent
        player_actions = board.get_legal_actions()
        board.modify_turn_color()
        opponent_actions = board.get_legal_actions()
        board.modify_turn_color()
        num_player_actions = len(player_actions)
        num_opponent_actions = len(opponent_actions)

        if player_color == self.color:
            num_extra_actions = num_player_actions - num_opponent_actions
        else:
            num_extra_actions = num_opponent_actions - num_player_actions

        # calculate how many more tokens the player has compared to the opponent
        num_player_tokens = board._player_token_count(self.color)
        num_opponent_tokens = board._player_token_count(self.color.opponent)
        num_extra_tokens = num_player_tokens - num_opponent_tokens

        utility = 0.5*num_extra_tokens + 0.5*num_extra_actions
        return utility






    


    
