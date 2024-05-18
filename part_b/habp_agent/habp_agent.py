import numpy as np
import time

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.tracktime import *
from utils.iterdeep_agent import *
from utils.orderchildren import *

# ______________________________________________________________________________
class NegamaxAgent(IterativeDeepeningAgent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)
        return

    def search(self, root: Node, board: Board, alpha, beta, depth, ply, time_remaining=None, move_values=None):
        alphaOrig = alpha
        
        entry: TTEntry = self.transposition_table.retrieve(board._state)
        if entry is not None and entry.depth >= depth:
            print("-------------------------visited-------------------------")
            if entry.node_type == EXACT:
                return entry.best_value, entry.best_child, move_values
            elif entry.node_type == LOWER_BOUND and entry.best_value > alpha:
                alpha = entry.best_value
            elif entry.node_type == UPPER_BOUND and entry.best_value < beta:
                beta = entry.best_value
            if alpha >= beta:
                return entry.best_value, entry.best_child, move_values
        
        if root.cutoff_test(depth):
            print(board.render(use_color=True))
            print("agent's color:", self.color)
            print("turn color:", board.turn_color)
            print("ply:", ply)
            utility_value = root.state_info.eval_fn(self.color, ply)
            print("utility_value:", utility_value)
            return utility_value, None, move_values
        
        best_child = None
        value = -np.inf
        children = root.get_all_children(board)
        children = OrderChildren.order_children(board, children, self.color, self.transposition_table, move_values)
        children = OrderChildren.topk_children(children)

        print("depth:", ply, "total number of children:", len((children)))

        start_time = time.time()
        for child_node in children:
            mutation = board.apply_action(child_node.parent_action)
            child_value, _, _ = self.search(child_node, board, -beta, -alpha, depth - 1, ply + 1, time_remaining, move_values)
            child_value = -child_value
            if child_value > value:
                value = child_value
                best_child = child_node
            alpha = max(alpha, value)
            board.undo_action(mutation)
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
        print("best_value:", value)
        move_values[board._state.__hash__()] = value
        self.transposition_table.store(board, node_type, depth, best_child, value)
        return value, best_child, move_values

        












        


    




    
