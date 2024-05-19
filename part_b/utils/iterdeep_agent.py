from utils.board import Board
from utils.constants import *
import time
from abc import *
from utils.node import *
from utils.table import *
import time
from utils.searchexit import *
import numpy as np
from utils.orderactions import *

class IterativeDeepeningAgent(ABC):
    def __init__(self, color) -> None:
        super().__init__()
        self.transposition_table = TranspositionTable()
        self.color = color # color of THE PLAYER (YOU)
        self.full_depth = True
        self.expire_time = None

    def best_action(self, board: Board, time_remaining):
        """
        Return the best action node. Different strategy is employed at different
        stage of the game.
        """
        # print("@ number of legal actions:", root.num_player_legal_actions)
        # print("@ number of empty coordinates:", root.num_empty_cells)
        legal_actions = board.get_legal_actions()
        # game_progress = len(legal_actions)
        game_progress = len(board._empty_coords())
        
        if board._turn_count == 0 or game_progress > EMPTY_THRESHOLD:
            # play a safe random move
            # print("%"*DELIM_LEN, "OPENING_GAME_STAGE", "%"*DELIM_LEN)
            best_action = random.choice(legal_actions)
        else:
            # complete principal variation search in endgame stage
            # print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
            start_time = time.time()
            expire_time = start_time + time_remaining/(MAX_TURNS - board._turn_count) + board._turn_count/TIME_OUT_FACTOR
            # print("allocated time:", expire_time - start_time)
            best_action = self.iterative_deepening_search(board, MAX_SEARCH_DEPTH, expire_time=expire_time)
               
        return best_action
    
    def iterative_deepening_search(self, board: Board, max_depth=MAX_SEARCH_DEPTH, expire_time=None):
        """
        Return the best action in a iterative deepening scheme. Search until the 
        time limit expires.
        """
        depth = 1
        self.expire_time = expire_time
        move_values = {}
        while depth < max_depth:
            # print("max depth:", depth)
            # print("size of transposition table:", len(self.transposition_table.table))
            # print("move_values:")
            # print(move_values)
            _, best_action, exit_type = self.search(board, -np.inf, np.inf, depth, 0, move_values)
            depth += 1
            if exit_type == SearchExit.TIME or exit_type == SearchExit.FULL_DEPTH:
                break
        self.full_depth = True
        return best_action
    
    @abstractmethod
    def search(self, board: Board, alpha, beta, depth, ply):
        """
        Return the best value, best action of the current node. Also returns an
        updated move values dictionary. Agent specific.
        """
        return NotImplementedError

    def has_time_left(self):
        return time.time() < self.expire_time
    
    def cutoff_test(self, board: Board, depth):
        return depth == 0 or (board.winner_color is not None)
    
    def alpha_beta_with_memory(self, board: Board, alpha, beta, depth, ply, move_values):
        """
        Return the best value, best action of the current node. Agent specific.
        """
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
            action_value, _, search_exit_type = self.alpha_beta_with_memory(board, -beta, -alpha, depth - 1, ply + 1, move_values)
            action_value = -action_value
            if action_value > value:
                value = action_value
                best_action = action
            alpha = max(alpha, value)
            board.undo_action(mutation)
            if alpha >= beta:
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

    
    