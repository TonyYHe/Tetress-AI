import numpy as np

from agent.board import Board
from copy import deepcopy
from habp_agent.utility import *
from referee.game.constants import MAX_TURNS

TURN_THRESHOLD = MAX_TURNS * 0.8 

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
        if self.cutoff_test(depth):
            return self.eval_fn()
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
        if self.cutoff_test(depth):
            return self.eval_fn()
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
    
    def cutoff_test(self, depth):
        d = 4
        return depth > d or self.state.game_over
    
    def eval_fn(self, game_over=False):
        """
        This is problematic.
        Return a positive utility value for the player, and a negative utility 
        value for the opponent.
        """
        if game_over == True:
            return self.state.game_result() * 1000
        
        board = self.state
        curr_color = board._turn_color

        # check if the utility of the current state has been calculated already
        board_dict = board._state
        key = board_dict
        utility = transposition_table.get(key)
        if utility is not None:
            return utility

        # Find the difference in the number of actions 
        extra_num_actions = diff_legal_actions(board, self.color)
        # Find the difference in the number of empty cells reachable that can be used as an action 
        extra_num_reachable = diff_reachable_valid_empty_cell(board, self.color)
        # Find the difference in the number of cells occupied 

        extra_num_occupied = diff_cells_occupied(board, self.color)
         # it's best to normalise this result to [-1, 1]
        if board.turn_count < TURN_THRESHOLD: 
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
        transposition_table[key] = utility
        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if self.color == curr_color else -utility




    
