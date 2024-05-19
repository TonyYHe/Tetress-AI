import numpy as np
from copy import deepcopy
import time

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.tracktime import *
from utils.iterdeep_agent import *

# ______________________________________________________________________________
class PVSAgent(IterativeDeepeningAgent):
    def __init__(self, board: Board, color: PlayerColor, parent_action=None):
        super().__init__(board, color, parent_action)
        return
    
    def search(self, root: Node, board: Board, alpha, beta, depth, ply, time_remaining=None, move_values=None):
        """
        Modified code from https://ics.uci.edu/~eppstein/180a/990202b.html
        Return the best child using Principle Variation Search. Utilises 
        transposition table to improve search efficiency.
        """
        
        alphaOrig = alpha
        
        entry: TTEntry = self.transposition_table.retrieve(board._state)
        if entry is not None and entry.depth >= depth:
            if entry.node_type == EXACT:
                return entry.best_value, entry.best_child, move_values
            elif entry.node_type == LOWER_BOUND and entry.best_value > alpha:
                alpha = entry.best_value
            elif entry.node_type == UPPER_BOUND and entry.best_value < beta:
                beta = entry.best_value
            if alpha >= beta:
                return entry.best_value, entry.best_child, move_values
        
        if root.cutoff_test(depth):
            return root.state_info.eval_fn(board, self.color, ply), None, move_values
        
        best_child = None
        value = -np.inf
        children = root.get_all_children(board, self.stateinfo_table, self.color==board._turn_color)
        children = Node.reorder_children(board, children, move_values)
        pv_node = children[0]
        start_time = time.time()

        for child_node in children:
            mutation = board.apply_action(child_node.parent_action)
            if pv_node == child_node:
                child_value, _, _ = self.search(child_node, board, -beta, -alpha, depth - 1, ply + 1, time_remaining, move_values)
            else:
                child_value, _, _ = self.search(board, -alpha-1, -alpha, depth - 1, ply + 1, time_remaining, move_values)
                if alpha < score and score < beta:
                    score = -self.search(board, -beta, -alpha, depth - 1, ply + 1, time_remaining, move_values)
            child_value = -child_value
            board.undo_action(mutation)
            if child_value > value:
                value = child_value
                best_child = child_node
            alpha = max(alpha, value)
            if alpha >= beta:
                break   

            time_remaining = time_left(time_remaining, start_time)     
            if time_remaining is not None and time_remaining <= 0:
                break
        
        node_type = EXACT
        if value <= alphaOrig:
            node_type = UPPER_BOUND
        elif value >= beta:
            node_type = LOWER_BOUND

        move_values[board._state.__hash__()] = value
        self.transposition_table.store(board, node_type, depth, best_child, value, root.state_info)

        return value, best_child, move_values











        


    




    
