import numpy as np

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.iterdeep_agent import *
from utils.orderactions import *
from utils.searchexit import *

# ______________________________________________________________________________
class MTDFAgent(IterativeDeepeningAgent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)
        return
    
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
        g = 0
        depth = 1
        self.expire_time = expire_time
        move_values = {}
        while depth < max_depth:
            # print("max depth:", depth)
            # print("size of transposition table:", len(self.transposition_table.table))
            # print("move_values:")
            # print(move_values)
            g, best_action, exit_type = self.search(board, g, depth, 0, move_values)
            depth += 1
            if exit_type == SearchExit.TIME or exit_type == SearchExit.FULL_DEPTH:
                break
        self.full_depth = True
        return best_action

    def search(self, board: Board, first_guess, depth, ply, move_values):
        g = first_guess
        best_action = None
        upper_bound = np.inf
        lower_bound = -np.inf
        while lower_bound < upper_bound:
            beta = max(g, lower_bound + 1)
            g, best_action, search_exit_type = self.alpha_beta_with_memory(board, beta-1, beta, depth - 1, ply + 1, move_values)
            if g < beta:
                upper_bound = g
            else:
                lower_bound = g
            if self.has_time_left() == False:
                search_exit_type = SearchExit.TIME
                break
        return g, best_action, search_exit_type










        


    




    
