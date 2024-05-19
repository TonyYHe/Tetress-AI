from utils.board import Board
from utils.constants import *
import time
from abc import *
from utils.node import *
from utils.table import *
import time
from utils.searchexit import *
import numpy as np

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
        game_progress = len(legal_actions)
        
        if board._turn_count == 0 or game_progress > MIDGAME_STAGE: 
            # play a safe random move
            # print("%"*DELIM_LEN, "OPENING_GAME_STAGE", "%"*DELIM_LEN)
            best_action = random.choice(legal_actions)
        else:
            # complete principal variation search in endgame stage
            # print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
            start_time = time.time()
            expire_time = start_time + LATEGAME_TIME + board._turn_count/TIME_OUT_FACTOR
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
        while depth < max_depth:
            # print("max depth:", depth)
            # print("size of transposition table:", len(self.transposition_table.table))
            # print("move_values:")
            # print(move_values)
            _, best_action, exit_type = self.search(board, -np.inf, np.inf, depth, 0)
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

    
    