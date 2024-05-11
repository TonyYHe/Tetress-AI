import numpy as np

from utils.board import Board
from copy import deepcopy
from utils.constants import *

transposition_table = dict()

# ______________________________________________________________________________
class HABPNode():
    def __init__(self, board: Board, color, parent_action=None):
        self.state = board
        self.color = color
        self.parent_action = parent_action
        self.children = dict()
        self.legal_actions = self.state.get_legal_actions()
        self.children_utilities = []
        self.num_legal_actions = len(self.legal_actions)
        self.num_empty_cells = len(self.state._empty_coords())
        self.game_over = self.state.game_over 
        return
    
    def sort_children(self, max=True):
        """
        Return sorted child nodes based on utility value. Sorts in descending 
        order if current node is MAX, otherwise sort in ascending order.
        """
        # Check if children_utilities has been calculated before
        if self.children_utilities != []:
            return self.children_utilities
        
        for a in self.legal_actions:
            new_board = deepcopy(self.state)
            new_board.apply_action(a)
            child_node = HABPNode(new_board, self.color, a)
            self.children[a] = child_node
            utility = self.eval_fn(self.game_over)
            self.children_utilities.append((child_node, utility))

        self.children_utilities.sort(key=lambda x:x[1], reverse=max)
                
        return self.top_k_children()
    
    def top_k_children(self):
        num_children = len(self.children_utilities)
        proportion = self.num_empty_cells / NUM_CELLS
        k = int(proportion * num_children)
        return self.children_utilities[:k]
        
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
        sorted_children = self.sort_children(max=True)

        print("ab's total # of children:", self.num_legal_actions, "top k children:", len(sorted_children))

        for child_node, _ in sorted_children:
            v = child_node.min_value(best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_child = child_node

        return best_child
    
    # Functions used by alpha_beta
    def max_value(self, alpha, beta, depth):
        if self.cutoff_test(depth):
            return self.eval_fn(game_over=self.game_over)
        
        v = -np.inf
        sorted_children = self.sort_children(max=True)

        print("MAX, depth:", depth, "total # of legal actions:", self.num_legal_actions, "top k children:", len(sorted_children))
        
        for child_node, _ in sorted_children:
            v = max(v, child_node.min_value(alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, alpha, beta, depth):
        if self.cutoff_test(depth):
            return self.eval_fn(game_over=self.game_over)
        
        v = np.inf
        sorted_children = self.sort_children(max=False)

        print("MIN, depth:", depth, "total # of legal actions:", self.num_legal_actions, "top k children:", len(sorted_children))

        for child_node, _ in sorted_children:
            v = min(v, child_node.max_value(alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v  
    
    def cutoff_test(self, depth):
        if self.game_over:
            return True
        if self.num_empty_cells > LATEGAME_STAGE:
            return depth > 0
        if self.num_empty_cells > ENDGAME_STAGE:
            return depth > 1
        return depth > 2
    
    def eval_fn(self, game_over):
        """
        This is problematic.
        Return a positive utility value for the player, and a negative utility 
        value for the opponent.
        """
        board = self.state
        player_color = self.color

        if game_over == True:
            return board.game_result(player_color) * 1000
        
        boardstate = board._state
        curr_color = board._turn_color

        # check if the utility of the current state has been calculated already
        utility = transposition_table.get(boardstate)
        if utility is not None:
            return utility

        # Find the difference in the number of actions 
        extra_num_actions = self.diff_legal_actions()
        # Find the difference in the number of cells occupied 
        extra_num_occupied = self.diff_cells_occupied()

         # it's best to normalise this result to [-1, 1]
        if board._turn_count < TURN_THRESHOLD: 
            # Far away from turns limitation 
            utility = extra_num_actions + extra_num_occupied * 0.1 
        else: 
            # If about to reach turns limit, evalution also include the number of cells occupied 
            turns_exceed_threshold = board._turn_count - TURN_THRESHOLD
            utility = extra_num_actions + extra_num_occupied * turns_exceed_threshold * 0.5 

        transposition_table[boardstate] = utility
        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if player_color == curr_color else -utility
    
    def diff_cells_occupied(self) -> int:
        """
        Find the difference in the number of tokens between the player and the 
        opponent. 
        """
        player_color = self.color
        num_player_occupied = self.state._player_token_count(player_color)
        num_opponent_occupied = self.state._player_token_count(player_color.opponent)
        return num_player_occupied - num_opponent_occupied


    def diff_legal_actions(self) -> int: 
        """
        Find the difference in the number of legal actions between the player and 
        the opponent. 
        """
        curr_color = self.state._turn_color
        player_color = self.color
        if curr_color == player_color:
            num_player_actions = self.num_legal_actions
            self.state.modify_turn_color(player_color.opponent)
            num_opponent_actions = len(self.state.get_legal_actions())
        else:
            num_opponent_actions = self.num_legal_actions
            self.state.modify_turn_color(player_color)
            num_player_actions = len(self.state.get_legal_actions())
        self.state.modify_turn_color(curr_color)
        return num_player_actions - num_opponent_actions

    




    
