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
        elif game_progress > LATEGAME_STAGE:
            # use heuristic alpha beta pruning in the lategame stage
            print("%"*DELIM_LEN, "MIDGAME_STAGE", "%"*DELIM_LEN)
            best_child = self.iterative_deepening_pvs(board, topk=True, time_remaining=board.turn_count/TIME_OUT_FACTOR)
        else:
            # complete alpha beta pruning in the endgame stage
            print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
            best_child = self.iterative_deepening_pvs(board, topk=False, time_remaining=board.turn_count/TIME_OUT_FACTOR)
        return best_child
    
    def get_children(self, board: Board, isMaximizingPlayer=True) -> dict:
        """
        Return child nodes stored in dict[action, PVSNode].
        """
        # Check if children has been generated already
        if self.children is not None:
            return self.children
        
        legal_actions = self.state_info.player_legal_actions if isMaximizingPlayer else self.state_info.opponent_legal_actions
        self.children = dict()
        for a in legal_actions:
            mutation = board.apply_action(a)
            child_node = PVSNode(board, self.color, a)
            self.children[a] = child_node
            board.undo_action(mutation)
        return self.children
    
    def iterative_deepening_pvs(self, board: Board, topk=False, time_remaining=None):
        depth = 1
        start_time = time.time()
        while depth < MAX_SEARCH_DEPTH + 1:
            print("max depth:", depth)
            _, best_child = self.PVS_alpha_beta_search(board, -np.inf, np.inf, depth, depth, topk, time_remaining)
            depth += 1
            time_remaining = time_left(time_remaining, start_time)
            if time_remaining is not None and time_remaining <= 0:
                break
        return best_child
    
    def topk_chldren(self):
        num_children = len(self.children)
        proportion = (NUM_CELLS - self.state_info.num_empty_cells) / NUM_CELLS
        k = int(proportion * num_children)
        k = min(k + 1, num_children)
        return self.ordered_children[:k]

    def PVS_alpha_beta_search(self, board: Board, alpha, beta, depth, max_depth, topk=False, time_remaining=None):
        """
        Modified code from https://ics.uci.edu/~eppstein/180a/990202b.html
        Return the best child using Principle Variation Search. Utilises 
        transposition table to improve search efficiency.
        """
        entry: TTEntry = transposition_table.retrieve(board._state)
        if entry is not None:
            if entry.depth >= depth:
                utility_value = entry.state_info.eval_fn(board, self.color, depth)
                if entry.node_type == EXACT:
                    return utility_value, entry.best_child
                elif entry.node_type == LOWER_BOUND and utility_value > alpha:
                    alpha = utility_value
                elif entry.node_type == UPPER_BOUND and utility_value < beta:
                    beta = utility_value
                if alpha >= beta:
                    return utility_value, entry.best_child
            
        if self.cutoff_test(depth):
            return self.state_info.eval_fn(board, self.color, depth), None
        
        start_time = time.time()
        best_value = -np.inf
        best_child = None
        self.get_children(board=board, isMaximizingPlayer=(board._turn_color==self.color))
        self.sort_children(board=board, isMaximizingPlayer=(board._turn_color==self.color), depth=max_depth-depth)
        pv_node = self.ordered_children[0]
        
        children = self.ordered_children
        print("depth:", max_depth-depth, "total number of children:", len(children))
        if topk == True:
            children = self.topk_chldren()
        
        print("top k:", len(children))
        for child_node in children:
            # print("color:", board._turn_color, "depth:", max_depth-depth, "before applying action:", child_node.parent_action)
            # print(board.render(use_color=True))
            mutation = board.apply_action(child_node.parent_action)
            # print("color:", board._turn_color, "depth:", max_depth-depth, "after applying action:", child_node.parent_action)
            # print(board.render(use_color=True))
            if pv_node == child_node:
                value = -child_node.PVS_alpha_beta_search(board, -beta, -alpha, depth - 1, max_depth, topk, time_remaining)[0]
            else:
                value = -child_node.PVS_alpha_beta_search(board, -alpha-1, -alpha, depth - 1, max_depth, topk, time_remaining)[0]
                if alpha < value and value < beta:
                    value = -child_node.PVS_alpha_beta_search(board, -beta, -alpha, depth - 1, max_depth, topk, time_remaining)[0]
            board.undo_action(mutation)
            # print("color:", board._turn_color, "depth:", max_depth-depth, "after reversing action:", child_node.parent_action)
            # print(board.render(use_color=True))
            if value >= best_value:
                best_value = value
                best_child = child_node
                alpha = max(alpha, value)
                if alpha >= beta:
                    break       
            time_remaining = time_left(time_remaining, start_time)     
            if time_remaining is not None and time_remaining <= 0:
                break
        
        node_type = EXACT
        if best_value <= alpha:
            node_type = UPPER_BOUND
        elif best_value >= beta:
            node_type = LOWER_BOUND
        transposition_table.store(board, node_type, depth, best_child, self.state_info)

        return best_value, best_child











        


    




    
