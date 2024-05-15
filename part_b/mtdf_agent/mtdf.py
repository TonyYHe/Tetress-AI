import numpy as np
from copy import deepcopy
import time

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.habp import *
from utils.tracktime import *

stateinfo_table = StateinfoTable()
transposition_table = TranspositionTable()
# ______________________________________________________________________________
class MTDFNode(HABPNode):
    def __init__(self, board: Board, color: PlayerColor, parent_action=None):
        super().__init__(board, color, parent_action)
        return

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
        # elif game_progress > LATEGAME_STAGE:
            # find the most promising move as in the case of the greedy agent in
            # midgame stage 
            # print("%"*DELIM_LEN, "MIDGAME_STAGE", "%"*DELIM_LEN)
            # self.get_children(board, isMaximizingPlayer=True)
            # self.sort_children(isMaximizingPlayer=True)
            # best_child = self.ordered_children[0]
        # elif game_progress > ENDGAME_STAGE:
        #     # use heuristic alpha beta pruning in the lategame stage
        #     print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
        #     best_child = self.iterative_deepening_mtdf(board, board.turn_count/TIME_OUT_FACTOR)
        else:
            # complete alpha beta pruning in the endgame stage
            print("%"*DELIM_LEN, "ENDGAME_STAGE", "%"*DELIM_LEN)
            best_child = self.iterative_deepening_mtdf(board, board.turn_count/TIME_OUT_FACTOR)
        return best_child
    
    def iterative_deepening_mtdf(self, board: Board, time_remaining=None):
        guess = 0
        best_child = None
        start_time = time.time()
        depth = 1
        while depth < MAX_SEARCH_DEPTH + 1:
            print("depth:", depth)
            guess, best_child = self.mtdf(board, guess, depth, time_remaining)
            depth += 1
            time_remaining = time_left(time_remaining, start_time)
            if time_remaining is not None and time_remaining <= 0:
                break
        return best_child
    
    def mtdf(self, board, first_guess, depth, time_remaining=None):
        g = first_guess
        best_child = None
        upper_bound = np.inf
        lower_bound = -np.inf
        start_time = time.time()            
        while lower_bound < upper_bound:
            beta = max(g, lower_bound + 1)
            g, best_child = self.alpha_beta_with_memory(board, beta - 1, beta, depth, time_remaining)
            if g < beta:
                upper_bound = g
            else:
                lower_bound = g
            time_remaining = time_left(time_remaining, start_time)
            if time_remaining is not None and time_remaining <= 0:
                break
        return g, best_child

    def alpha_beta_with_memory(self, board: Board, alpha, beta, depth, time_remaining=None):

        if self.cutoff_test(depth):
            return self.state_info.eval_fn(board, self.color), None
        
        entry: TTEntry = transposition_table.retrieve(board._state)
        if entry is not None:
            if entry.depth >= depth:
                utility_value = entry.state_info.eval_fn(board, self.color)
                if entry.node_type == EXACT:
                    return utility_value, entry.best_child
                elif entry.node_type == LOWER_BOUND and utility_value > alpha:
                    alpha = utility_value
                elif entry.node_type == UPPER_BOUND and utility_value < beta:
                    beta = utility_value
                if alpha >= beta:
                    return utility_value, entry.best_child
        
        best_value = -np.inf
        best_child = None
        start_time = time.time()
        self.get_children(board=board, isMaximizingPlayer=(board._turn_color==self.color))
        self.sort_children(board=board, isMaximizingPlayer=(board._turn_color==self.color))
        for child_node in self.ordered_children:
            mutation = board.apply_action(child_node.parent_action)
            value, _ = self.alpha_beta_with_memory(board, -beta, -alpha, depth - 1, time_remaining)
            board.undo_action(mutation)
            if value > best_value:
                best_value = value
                best_child = child_node
            alpha = max(alpha, value)
            if alpha >= beta:
                break
            time_remaining = time_left(time_remaining, start_time)
            if time_remaining is not None and time_remaining <= 0:
                break
        
        if best_value <= alpha:
            node_type = UPPER_BOUND
        elif best_value >= beta:
            node_type = LOWER_BOUND
        else:
            node_type = EXACT
        transposition_table.store(board, node_type, depth, best_child, self.state_info)
        return best_value, best_child











        


    




    
