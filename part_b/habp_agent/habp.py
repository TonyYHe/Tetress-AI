import numpy as np

from utils.board import *
from copy import deepcopy
from utils.constants import *
import random
from habp_agent.transtable import TranspositionTable
import time

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
        Sort child nodes based on utility value. Sorts in descending order if 
        current node is MAX, otherwise sort in ascending order.
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
                    
    def best_child(self, board: Board, time_remaining):
        """
        Return the best child node.
        """
        print("@ number of legal actions:", self.state_info.num_player_legal_actions)
        print("@ number of empty coordinates:", self.state_info.num_empty_cells)
        board = deepcopy(board)
        game_progress = self.state_info.num_empty_cells
        if game_progress > MIDGAME_STAGE: 
            # play a safe random move
            print("%"*DELIM_LEN, "OPENING_GAME_STAGE", "%"*DELIM_LEN)
            best_child = self.get_safe_random_child(board)
        elif game_progress > LATEGAME_STAGE:
            # find the most promising move as in the case of the greedy agent in
            # midgame stage 
            print("%"*DELIM_LEN, "MIDGAME_STAGE", "%"*DELIM_LEN)
            self.sort_children(board, max=True)
            best_child = self.ordered_children[0]
        elif game_progress > ENDGAME_STAGE:
            # use heuristic alpha beta pruning in the lategame stage
            print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
            best_child = self.iterative_deepening(board, 4)
        else:
            # complete alpha beta pruning in the endgame stage
            print("%"*DELIM_LEN, "ENDGAME_STAGE", "%"*DELIM_LEN)
            best_child = self.iterative_deepening(board, MAX_TURNS)
        return best_child
    
    def get_safe_random_child(self, board: Board):
        """
        Return a random child that makes a safe move. A safe move is defined as
        take an action that increases the number of legal actions.
        """
        safe = False
        start_time = time.time()
        while not safe and time.time() - start_time < 0.5:
            random_action = random.choice(self.state_info.player_legal_actions)
            mutation = board.apply_action(random_action)
            random_child = HABPNode(board, self.color, list(), parent_action=random_action)
            board.undo_action(mutation)
            safe = random_child.state_info.num_player_legal_actions > self.state_info.num_player_legal_actions

        return random_child
        
    def iterative_deepening(self, board: Board, max_depth: int):
        best_child = None
        best_score = -np.inf
        start_time = time.time()
        depth = 1
        while time.time() - start_time < board._turn_count / TIME_OUT_FACTOR and depth < max_depth:
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
            depth += 1
        return best_child
                
    def alpha_beta_with_move_ordering(self, board: Board, depth, alpha, beta, maximizing_player):
        if self.cutoff_test(depth):
            return self.state_info.utility_value
        
        self.sort_children(board, max=maximizing_player)
        if maximizing_player:
            value = -np.inf
            for child_node in self.ordered_children:
                new_board = child_node.get_current_board(board)
                value = max(value, self.alpha_beta_with_move_ordering(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = np.inf
            for child_node in self.ordered_children:
                new_board = child_node.get_current_board(board)
                value = min(value, self.alpha_beta_with_move_ordering(new_board, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value
        
    def top_k_children(self):
        num_children = len(self.ordered_children)
        proportion = self.state_info.num_empty_cells / NUM_CELLS
        k = min(int(proportion * num_children) + 10, num_children)
        return self.ordered_children[:k]

    def cutoff_test(self, depth):
        return depth == 0 or self.state_info.game_over
    
    def get_current_board(self, board: Board):
        """
        Apply mutations to get the current board state. Return the new board
        state.
        """
        for board_mutation in self.mutations:
            board.apply_action(board_mutation.action)
            # print("apply action:", board_mutation.action)
        return board

    def get_old_board(self, board: Board):
        """
        Undo mutations to get the original board state. Return the reversed 
        board state.
        """
        for board_mutation in self.mutations[::-1]:
            board.undo_action(board_mutation)
            # print("reverse action:", board_mutation.action)
        return board

    




    
