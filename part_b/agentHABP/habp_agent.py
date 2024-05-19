import numpy as np
import time

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.iterdeep_agent import *
from utils.orderchildren import *
from utils.searchexit import *

# ______________________________________________________________________________
class NegamaxAgent(IterativeDeepeningAgent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)
        return

    def search(self, root: Node, board: Board, alpha, beta, depth, ply):
        entry: TTEntry = self.transposition_table.retrieve(board._state)
        if entry is not None and entry.depth >= depth:
            # print("-------------------------visited-------------------------")
            if entry.node_type == EXACT:
                return entry.best_value, entry.best_child, SearchExit.DEPTH
            elif entry.node_type == LOWER_BOUND and entry.best_value > alpha:
                alpha = entry.best_value
            elif entry.node_type == UPPER_BOUND and entry.best_value < beta:
                beta = entry.best_value
            if alpha >= beta:
                return entry.best_value, entry.best_child, SearchExit.DEPTH
        
        if root.cutoff_test(depth):

            utility_value = root.state_info.eval_fn(board._turn_color, ply)

            # print(board.render(use_color=True))
            # print("agent's color:", self.color)
            # print("turn color:", board.turn_color)
            # print("ply:", ply)
            # print("utility_value:", utility_value)

            if utility_value <= alpha:
                self.transposition_table.store(board, LOWER_BOUND, depth, None, utility_value)
            elif utility_value >= beta:
                self.transposition_table.store(board, UPPER_BOUND, depth, None, utility_value)
            else:
                self.transposition_table.store(board, EXACT, depth, None, utility_value)
            
            if self.full_depth == False:
                search_exit_type = SearchExit.DEPTH
            elif board.game_over != True:
                self.full_depth = False
                search_exit_type = SearchExit.DEPTH
            else:
                search_exit_type = SearchExit.FULL_DEPTH

            return utility_value, None, search_exit_type
        
        best_child = None
        value = -np.inf
        children = root.get_all_children(board)
        children = OrderChildren.order_children(board, children, self.color, self.transposition_table)
        children = OrderChildren.topk_children(children)

        # print("depth:", ply, "total number of children:", len((children)))

        for child_node in children:
            mutation = board.apply_action(child_node.parent_action)
            child_value, _, search_exit_type = self.search(child_node, board, -beta, -alpha, depth - 1, ply + 1)
            child_value = -child_value
            if child_value > value:
                value = child_value
                best_child = child_node
            alpha = max(alpha, value)
            board.undo_action(mutation)
            if alpha >= beta:
                break   

            if self.has_time_left() == False:
                search_exit_type = SearchExit.TIME
                break

        node_type = EXACT
        if value <= alpha:
            node_type = LOWER_BOUND
        elif value >= beta:
            node_type = UPPER_BOUND

        # print("best_value:", value)
        self.transposition_table.store(board, node_type, depth, best_child, value)
        return value, best_child, search_exit_type

        












        


    




    