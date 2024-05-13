import numpy as np

from utils.board import Board
from copy import deepcopy
from utils.constants import *
import random
from habp_agent.transtable import TranspositionTable

transposition_table = TranspositionTable()
# ______________________________________________________________________________
class HABPNode():
    def __init__(self, board: Board, color, mutations: list=[], parent_action=None):
        self.color = color
        self.mutations = mutations
        self.parent_action = parent_action
        self.children = dict()
        self.children_utilities = []
        self.legal_actions = board.get_legal_actions() # doesn't alway correspond to board
        self.num_legal_actions = len(self.legal_actions)
        self.num_empty_cells = len(board._empty_coords())
        self.game_over = board.game_over 
        return
    
    def sort_children(self, board: Board, max=True):
        """
        Return sorted child nodes based on utility value. Sorts in descending 
        order if current node is MAX, otherwise sort in ascending order.
        """
        # Check if children_utilities has been calculated before
        if self.children_utilities != []:
            return self.children_utilities
        
        for a in self.legal_actions:
            # print("root:")
            # print(board.render(use_color=True))
            self.get_current_board(board)
            # print("current:")
            # print(board.render(use_color=True))
            # print("action:", a)
            mutation = board.apply_action(a)
            # print("After applying action:")
            # print(board.render(use_color=True))
            child_node = HABPNode(board, self.color, self.mutations + [mutation], a)
            self.children[a] = child_node
            utility = child_node.eval_fn(board, child_node.game_over)
            self.children_utilities.append((child_node, utility))
            board.undo_action(mutation)
            # print("reversed:")
            # print(board.render(use_color=True))
            self.get_old_board(board)

        self.children_utilities.sort(key=lambda x:x[1], reverse=max)
                    
    def best_child(self, board: Board):
        print("# of legal actions:: ", self.num_legal_actions)
        print("# of empty coordinates:", self.num_empty_cells)
        board = deepcopy(board)
        game_progress = self.num_empty_cells
        if game_progress > MIDGAME_STAGE: 
            # play random moves in the opening stage
            best_action = random.choice(self.legal_actions)
            board.apply_action(best_action)
            best_child = HABPNode(board, self.color, list(), parent_action=best_action)
        elif game_progress > LATEGAME_STAGE:
            # find the most promising move as in the case of the greedy agent in
            # midgame stage 
            self.sort_children(board, max=True)
            best_child = self.children_utilities[0][0]
        elif game_progress > ENDGAME_STAGE:
            # use heuristic alpha beta pruning in the lategame stage
            print("LateGame Stage")
        else:
            # complete alpha beta pruning in the endgame stage
            print("EndGame Stage")
        return best_child
    
    def top_k_children(self):
        """problematic, too simple"""
        num_children = len(self.children_utilities)
        proportion = self.num_empty_cells / NUM_CELLS
        k = int(proportion * num_children)
        return self.children_utilities[:k]
        
    def alpha_beta_cutoff_search(self, board: Board):
        """Search game to determine best action; use alpha-beta pruning.
        This version cuts off search and uses an evaluation function.
        Assumes the player is MAX.
        """

        # Body of alpha_beta_cutoff_search starts here:
        # The default test cuts off at depth d or at a terminal state
        best_score = -np.inf
        beta = np.inf
        best_child = None # ============ this is where the problem comes from =============
        self.sort_children(board, max=True)
        top_k_children = self.top_k_children()

        print("ab's total # of children:", self.num_legal_actions, "top k children:", len(top_k_children))

        for child_node, _ in top_k_children:
            v = child_node.min_value(best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_child = child_node

        return best_child
    
    # Functions used by alpha_beta
    def max_value(self, board: Board, alpha, beta, depth):
        if self.cutoff_test(depth):
            return self.eval_fn(board, game_over=self.game_over)
        
        v = -np.inf
        sorted_children = self.sort_children(board, max=True)

        print("MAX, depth:", depth, "total # of legal actions:", self.num_legal_actions, "top k children:", len(sorted_children))
        
        for child_node, _ in sorted_children:
            v = max(v, child_node.min_value(alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, board: Board, alpha, beta, depth):
        if self.cutoff_test(depth):
            return self.eval_fn(board, game_over=self.game_over)
        
        v = np.inf
        sorted_children = self.sort_children(board, max=False)

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
    
    def get_current_board(self, board: Board):
        """Apply mutations to get the current board state"""
        for board_mutation in self.mutations:
            board.apply_action(board_mutation.action)
            # print("apply action:", board_mutation.action)
        return board

    def get_old_board(self, board: Board):
        for board_mutation in self.mutations[::-1]:
            board.undo_action(board_mutation)
            # print("reverse action:", board_mutation.action)
        return board
    
    def eval_fn(self, board: Board, game_over: bool):
        """
        This is problematic.
        Return a positive utility value for the player, and a negative utility 
        value for the opponent.
        """
        
        player_color = self.color

        if game_over == True:
            return board.game_result(player_color) * 1000
        
        boardstate = board._state
        curr_color = board._turn_color

        # check if the utility of the current state has been calculated already
        utility = transposition_table.retrieve(boardstate)
        if utility is not None:
            return utility

        # Find the difference in the number of actions 
        extra_num_actions = self.diff_legal_actions(board)
        # Find the difference in the number of cells occupied 
        extra_num_occupied = self.diff_cells_occupied(board)

         # it's best to normalise this result to [-1, 1]
        if board._turn_count < TURN_THRESHOLD: 
            # Far away from turns limitation 
            utility = extra_num_actions + extra_num_occupied * 0.1 
        else: 
            # If about to reach turns limit, evalution also include the number of cells occupied 
            turns_exceed_threshold = board._turn_count - TURN_THRESHOLD
            utility = extra_num_actions + extra_num_occupied * turns_exceed_threshold * 0.5 

        transposition_table.store(boardstate, utility)
        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if player_color != curr_color else -utility
    
    def diff_cells_occupied(self, board: Board) -> int:
        """
        Find the difference in the number of tokens between the player and the 
        opponent. 
        """
        player_color = self.color
        num_player_occupied = board._player_token_count(player_color)
        num_opponent_occupied = board._player_token_count(player_color.opponent)
        return num_player_occupied - num_opponent_occupied


    def diff_legal_actions(self, board: Board) -> int: 
        """
        Find the difference in the number of legal actions between the player and 
        the opponent. 
        """
        curr_color = board._turn_color
        player_color = self.color
        if curr_color == player_color:
            num_player_actions = self.num_legal_actions
            board.modify_turn_color(player_color.opponent)
            num_opponent_actions = len(board.get_legal_actions())
        else:
            num_opponent_actions = self.num_legal_actions
            board.modify_turn_color(player_color)
            num_player_actions = len(board.get_legal_actions())
        board.modify_turn_color(curr_color)
        return num_player_actions - num_opponent_actions

    




    
