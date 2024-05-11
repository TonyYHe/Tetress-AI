import numpy as np

from utils.board import Board
from copy import deepcopy
from utils.eval_fn import *

transposition_table = dict()

# ______________________________________________________________________________
class HABPNode():
    def __init__(self, board: Board, color, parent=None, parent_action=None):
        self.state = board
        self.color = color
        self.parent = parent
        self.parent_action = parent_action
        self.children = dict()
        self.children_utilities = []
        return
    
    def sort_children(self, legal_actions, max=True):
        """Move ordering."""

        # Check if children_utilities has been calculated before
        if self.children_utilities != []:
            return self.children_utilities

        for a in legal_actions:
            new_board = deepcopy(self.state)
            new_board.apply_action(a)
            child_node = HABPNode(new_board, self.color, self, a)
            self.children[a] = child_node
            utility = child_node.eval_fn()
            self.children_utilities.append((child_node, utility))

        self.children_utilities.sort(key=lambda x:x[1], reverse=max)
                
        return self.children_utilities


    def alpha_beta_cutoff_search(self):
        """Search game to determine best action; use alpha-beta pruning.
        This version cuts off search and uses an evaluation function.
        Assumes the player is MAX.
        """

        # Body of alpha_beta_cutoff_search starts here:
        # The default test cuts off at depth d or at a terminal state
        best_score = -np.inf
        beta = np.inf
        best_child = None
        legal_actions = self.state.get_legal_actions()
        sorted_children = self.sort_children(legal_actions, max=True)

        print("ab number of legal actions:", len(legal_actions))

        for child_node, _ in sorted_children:
            v = child_node.min_value(best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_child = child_node
        return best_child
    
    # Functions used by alpha_beta
    def max_value(self, alpha, beta, depth):
        if self.cutoff_test1():
            return eval_fn(self.state, self.color, transposition_table, game_over=True)
        if self.cutoff_test2(depth):
            return eval_fn(self.state, self.color, transposition_table, game_over=False)
        
        v = -np.inf
        legal_actions = self.state.get_legal_actions()
        sorted_children = self.sort_children(legal_actions, max=True)

        print("max, depth:", depth, "number of legal actions:", len(legal_actions))
        
        for child_node, _ in sorted_children:
            v = max(v, child_node.min_value(alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, alpha, beta, depth):
        if self.cutoff_test1():
            return eval_fn(self.state, self.color, transposition_table, game_over=True)
        if self.cutoff_test2(depth):
            return eval_fn(self.state, self.color, transposition_table, game_over=False)
        
        v = np.inf
        legal_actions = self.state.get_legal_actions()
        sorted_children = self.sort_children(legal_actions, max=False)

        print("min, depth:", depth, "number of legal actions:", len(legal_actions))

        for child_node, _ in sorted_children:
            v = min(v, child_node.max_value(alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v  
    
    def cutoff_test1(self):
        return self.state.game_over      
    
    def cutoff_test2(self, depth):
        d = 4
        return depth > d




    
