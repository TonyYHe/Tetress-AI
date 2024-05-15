import numpy as np
from copy import deepcopy
import time

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.habp import *

stateinfo_table = StateinfoTable()
transposition_table = TranspositionTable()
# ______________________________________________________________________________
class PVSNode(HABPNode):
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
            # best_child = self.ordered_children[0]s
        # elif game_progress > ENDGAME_STAGE:
        #     # use heuristic alpha beta pruning in the lategame stage
        #     print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
        #     best_child = self.iterative_deepening_mtd_f(board, board.turn_count/TIME_OUT_FACTOR)
        else:
            # complete alpha beta pruning in the endgame stage
            print("%"*DELIM_LEN, "ENDGAME_STAGE", "%"*DELIM_LEN)
            best_child = self.iterative_deepening_pvs(board, board.turn_count/TIME_OUT_FACTOR)
        return best_child

    def iterative_deepening_pvs(self, board: Board, time_remaining=None):
        depth = 1
        start_time = time.time()
        while depth < MAX_SEARCH_DEPTH + 1 and time_remaining > 0:
            print("depth:", depth)
            _, best_child = self.PVS_alpha_beta_search(board, -np.inf, np.inf, depth, time_remaining)
            depth += 1
            elapsed_time = time.time() - start_time
            time_remaining -= elapsed_time
        return best_child
    
    def PVS_alpha_beta_search(self, board: Board, alpha, beta, depth, time_remaining=None):
        """
        Modified code from https://ics.uci.edu/~eppstein/180a/990202b.html
        Return the best child using Principle Variation Search. Utilises 
        transposition table to improve search efficiency.
        """
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
            
        if self.cutoff_test(depth):
            return self.state_info.eval_fn(board, self.color), None
        
        start_time = time.time()
        best_value = -np.inf
        best_child = None
        self.get_children(board=board, isMaximizingPlayer=(board._turn_color==self.color))
        self.sort_children(board=board, isMaximizingPlayer=(board._turn_color==self.color))
        pv_node = self.ordered_children[0]
        for child_node in self.ordered_children:
            mutation = board.apply_action(child_node.parent_action)
            if pv_node == child_node:
                value = -self.PVS_alpha_beta_search(board, -beta, -alpha, depth - 1, time_remaining)[0]
            else:
                value = -self.PVS_alpha_beta_search(board, -alpha-1, -alpha, depth - 1, time_remaining)[0]
                if alpha < value and value < beta:
                    value = -self.PVS_alpha_beta_search(board, -beta, -alpha, depth - 1, time_remaining)[0]
            board.undo_action(mutation)
            if value >= best_value:
                best_value = value
                best_child = child_node
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            if time_remaining is not None:
                elapsed_time = time.time() - start_time
                time_remaining -= elapsed_time
                if time_remaining <= 0:
                    break
        
        node_type = EXACT
        if best_value <= alpha:
            node_type = UPPER_BOUND
        elif best_value >= beta:
            node_type = LOWER_BOUND
        transposition_table.store(board, node_type, depth, best_child, self.state_info)

        return best_value, best_child











        


    




    
