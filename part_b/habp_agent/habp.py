import numpy as np

from utils.board import *
from copy import deepcopy
from utils.constants import *
import random
from habp_agent.transtable import TranspositionTable
from habp_agent.stateinfo import StateInformation

transposition_table = TranspositionTable()
# ______________________________________________________________________________
class HABPNode():
    def __init__(self, board: Board, color: PlayerColor, mutations: list=[], parent_action=None):
        self.color = color
        self.mutations = mutations
        self.parent_action = parent_action
        self.children = dict()
        self.ordered_children = []
        self.state_info = transposition_table.retrieve(board._state)
        if self.state_info is None:
            self.state_info = transposition_table.store(board, color)
        return
    
    def sort_children(self, board: Board, max=True):
        """
        Return sorted child nodes based on utility value. Sorts in descending 
        order if current node is MAX, otherwise sort in ascending order.
        """
        # Check if children has been sorted already
        if self.ordered_children != []:
            return
        
        legal_actions = self.state_info.player_legal_actions if max else self.state_info.opponent_legal_actions
        
        for a in legal_actions:
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
            self.ordered_children.append(child_node)
            board.undo_action(mutation)
            # print("reversed:")
            # print(board.render(use_color=True))
            self.get_old_board(board)

        self.ordered_children.sort(key=lambda x: x.state_info.utility_value, reverse=max)
                    
    def best_child(self, board: Board):
        print("# of legal actions:: ", self.state_info.num_player_legal_actions)
        print("# of empty coordinates:", self.state_info.num_empty_cells)
        board = deepcopy(board)
        game_progress = self.state_info.num_empty_cells
        if game_progress > MIDGAME_STAGE: 
            # play random moves in the opening stage
            # print("previous:")
            # print(board.render(use_color=True))
            best_action = random.choice(self.state_info.player_legal_actions)
            board.apply_action(best_action)
            # print("current:")
            # print(board.render(use_color=True))
            best_child = HABPNode(board, self.color, list(), parent_action=best_action)
        elif game_progress > LATEGAME_STAGE:
            # find the most promising move as in the case of the greedy agent in
            # midgame stage 
            self.sort_children(board, max=True)
            best_child = self.ordered_children[0]
        elif game_progress > ENDGAME_STAGE:
            # use heuristic alpha beta pruning in the lategame stage
            print("LateGame Stage")
        else:
            # complete alpha beta pruning in the endgame stage
            print("EndGame Stage")
        return best_child
    
    def iterative_deepening(self, board: Board, max_depth: int):
        best_child = None
        best_score = -np.inf

        for depth in range(1, max_depth + 1):
            current_best_score = -np.inf
            current_best_child = None
            self.sort_children(board, self.color)
            for child_node in self.ordered_children:
                new_board = child_node.get_current_board(board)
                score = -self.alpha_beta_with_move_ordering(new_board, depth - 1, -np.inf, np.inf, False)
                if score > current_best_score:
                    current_best_score = score
                    current_best_child = child_node
            if current_best_score > best_score:
                best_score = current_best_score
                best_child = current_best_child
        return best_child
                
    def alpha_beta_with_move_ordering(self, board: Board, depth, alpha, beta, maximizing_player):
        if self.cutoff_test(depth):
            return self.state_info.utility_value
        
        self.sort_children(board, max=maximizing_player)
        if maximizing_player:
            value = np.inf
            for child_node in self.ordered_children:
                new_board = child_node.get_current_board(board)
                value = max(value, self.alpha_beta_with_move_ordering(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = -np.inf
            for child_node in self.ordered_children:
                new_board = child_node.get_current_board(board)
                value = min(value, self.alpha_beta_with_move_ordering(new_board, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value
        
    # def top_k_children(self):
    #     """problematic, too simple"""
    #     num_children = len(self.children_utilities)
    #     proportion = self.num_empty_cells / NUM_CELLS
    #     k = int(proportion * num_children)
    #     return self.children_utilities[:k]

    # def old_alpha_beta_cutoff_search(self, board: Board):
    #     """Search game to determine best action; use alpha-beta pruning.
    #     This version cuts off search and uses an evaluation function.
    #     Assumes the player is MAX.
    #     """

    #     # Body of alpha_beta_cutoff_search starts here:
    #     # The default test cuts off at depth d or at a terminal state
    #     best_score = -np.inf
    #     beta = np.inf
    #     best_child = None # ============ this is where the problem comes from =============
    #     self.sort_children(board, max=True)
    #     top_k_children = self.top_k_children()

    #     print("ab's total # of children:", self.num_legal_actions, "top k children:", len(top_k_children))

    #     for child_node, _ in top_k_children:
    #         v = child_node.min_value(best_score, beta, 1)
    #         if v > best_score:
    #             best_score = v
    #             best_child = child_node

    #     return best_child
    
    # # Functions used by alpha_beta
    # def max_value(self, board: Board, alpha, beta, depth):
    #     if self.cutoff_test(depth):
    #         return self.eval_fn(board, game_over=self.game_over)
        
    #     v = -np.inf
    #     sorted_children = self.sort_children(board, max=True)

    #     print("MAX, depth:", depth, "total # of legal actions:", self.num_legal_actions, "top k children:", len(sorted_children))
        
    #     for child_node, _ in sorted_children:
    #         v = max(v, child_node.min_value(alpha, beta, depth + 1))
    #         if v >= beta:
    #             return v
    #         alpha = max(alpha, v)
    #     return v

    # def min_value(self, board: Board, alpha, beta, depth):
    #     if self.cutoff_test(depth):
    #         return self.eval_fn(board, game_over=self.game_over)
        
    #     v = np.inf
    #     sorted_children = self.sort_children(board, max=False)

    #     print("MIN, depth:", depth, "total # of legal actions:", self.num_legal_actions, "top k children:", len(sorted_children))

    #     for child_node, _ in sorted_children:
    #         v = min(v, child_node.max_value(alpha, beta, depth + 1))
    #         if v <= alpha:
    #             return v
    #         beta = min(beta, v)
    #     return v

    # def old_cutoff_test(self, depth):
    #     if self.state_info.game_over:
    #         return True
    #     if self.state_info.num_empty_cells > LATEGAME_STAGE:
    #         return depth > 0
    #     if self.state_info.num_empty_cells > ENDGAME_STAGE:
    #         return depth > 1
    #     return depth > 2  
    
    def cutoff_test(self, depth):
        return depth == 0 or self.state_info.game_over
    
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

    




    
