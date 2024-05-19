from utils.board import Board
from utils.constants import *
import time
from abc import *
from utils.node import *
from utils.table import *
import time
from utils.searchexit import *

class IterativeDeepeningAgent(ABC):
    def __init__(self, color) -> None:
        super().__init__()
        self.transposition_table = TranspositionTable()
        self.color = color # color of THE PLAYER (YOU)
        self.full_depth = True
        self.expire_time = None

    def best_child(self, root: Node, board: Board, time_remaining):
        """
        Return the best child node. Different strategy is employed at different
        stage of the game.
        """
        print("@ number of legal actions:", root.state_info.num_player_legal_actions)
        print("@ number of empty coordinates:", root.state_info.num_empty_cells)
        game_progress = root.state_info.num_player_legal_actions
        if board._turn_count == 0 or game_progress > MIDGAME_STAGE: 
            # play a safe random move
            print("%"*DELIM_LEN, "OPENING_GAME_STAGE", "%"*DELIM_LEN)
            best_child = root.get_safe_random_child(board)
        else:
            # complete principal variation search in endgame stage
            print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
            start_time = time.time()
            expire_time = start_time + LATEGAME_TIME + board._turn_count/TIME_OUT_FACTOR
            print("allocated time:", expire_time - start_time)
            best_child = self.iterative_deepening_search(root, board, MAX_SEARCH_DEPTH, expire_time=expire_time)
        return best_child
    
    def iterative_deepening_search(self, root: Node, board: Board, max_depth=MAX_SEARCH_DEPTH, expire_time=None):
        """
        Return the best child in a iterative deepening scheme. Search until the 
        time limit expires.
        """
        depth = 1
        move_values = {}
        self.expire_time = expire_time
        while depth < max_depth:
            print("max depth:", depth)
            print("size of transposition table:", len(self.transposition_table.table))
            print("move_values:")
            print(move_values)
            _, best_child, move_values, exit_type = self.search(root, board, -np.inf, np.inf, depth, 0, move_values)
            depth += 1
            if exit_type == SearchExit.TIME or exit_type == SearchExit.FULL_DEPTH:
                break
        self.full_depth = True
        return best_child
    
    @abstractmethod
    def search(self, root: Node, board: Board, alpha, beta, depth, ply, move_values=None):
        """
        Return the best value, best child of the current node. Also returns an
        updated move values dictionary. Agent specific.
        """
        return NotImplementedError

    def has_time_left(self):
        return time.time() < self.expire_time
    