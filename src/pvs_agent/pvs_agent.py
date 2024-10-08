import numpy as np

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.iterdeep_agent import *
from utils.orderactions import *
from utils.searchexit import *

# ______________________________________________________________________________
class PVSAgent(IterativeDeepeningAgent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)
        return

    def search(self, board: Board, alpha, beta, depth, ply, move_values):
        entry: TTEntry = self.transposition_table.retrieve(board._state)
        if entry is not None and entry.depth >= depth:
            # print("-------------------------visited-------------------------")
            if entry.node_type == EXACT:
                return entry.best_value, entry.best_action, SearchExit.DEPTH
            elif entry.node_type == LOWER_BOUND and entry.best_value > alpha:
                alpha = entry.best_value
            elif entry.node_type == UPPER_BOUND and entry.best_value < beta:
                beta = entry.best_value
            if alpha >= beta:
                return entry.best_value, entry.best_action, SearchExit.DEPTH
        
        if self.cutoff_test(board, depth):
            utility_value = board.eval_fn(ply)

            print(board.render(use_color=True))
            print("agent's color:", self.color)
            print("turn color:", board.turn_color)
            print("ply:", ply)
            print("utility_value:", utility_value)

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
        
        best_action = None
        value = -np.inf
        actions = board.get_legal_actions()
        actions = OrderActions.order_actions(board, actions, self.transposition_table, move_values)
        actions = OrderActions.topk_actions(actions)
        pv_action = actions[0]

        # print("depth:", ply, "total number of actions", len((actions)))

        for action in actions:
            mutation = board.apply_action(action)
            if action == pv_action:
                action_value, best_action, search_exit_type = self.search(board, -beta, -alpha, depth - 1, ply + 1, move_values)
            else:
                action_value, _, search_exit_type = self.search(board, -alpha-1, -alpha, depth - 1, ply + 1, move_values)
                if action_value < -alpha and action_value > -beta:
                    action_value, _, search_exit_type = self.search(board, -beta, -alpha, depth - 1, ply + 1, move_values)
            action_value = -action_value
            board.undo_action(mutation)
            if action_value >= value:
                value = action_value
                best_action = action
            alpha = max(action_value, alpha)
            if action_value >= beta:
                print("----------------- prunned", len(actions)-actions.index(action)-1, "nodes")
                break
            print("action:", action, "action_value:", action_value)
            if self.has_time_left() == False:
                search_exit_type = SearchExit.TIME
                break

        node_type = EXACT
        if value <= alpha:
            node_type = LOWER_BOUND
        elif value >= beta:
            node_type = UPPER_BOUND

        print("best_action:", best_action, "best_value:", value)
        move_values[board._state.__hash__()] = value
        self.transposition_table.store(board, node_type, depth, best_action, value)
        return value, best_action, search_exit_type











        


    




    
