from utils.board import Board
from utils.constants import *
from utils.tracktime import *
import time
from abc import *
from utils.node import *
from utils.table import *

class IterativeDeepeningAgent(ABC):
    def __init__(self, color) -> None:
        super().__init__()
        self.transposition_table = TranspositionTable()
        self.color = color # color of the player

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
            allocated_time = LATEGAME_TIME + board._turn_count/TIME_OUT_FACTOR
            print("allocated time:", allocated_time)
            best_child = self.iterative_deepening_search(root, board, MAX_SEARCH_DEPTH, time_remaining=allocated_time)
        return best_child
    
    def iterative_deepening_search(self, root: Node, board: Board, max_depth=MAX_SEARCH_DEPTH, time_remaining=None):
        """
        Return the best child in a iterative deepening scheme. Search until the 
        time limit expires.
        """
        start_time = time.time()
        depth = 1
        move_values = {}
        while depth < max_depth:
            print("max depth:", depth)
            print("size of transposition table:", len(self.transposition_table.table))
            print("move_values:")
            print(move_values)
            _, best_child, move_values = self.search(root, board, -np.inf, np.inf, depth, 0, time_remaining, move_values)
            depth += 1
            time_remaining = time_left(time_remaining, start_time)
            if time_remaining is not None and time_remaining <= 0:
                break
        return best_child
    
    @abstractmethod
    def search(self, root: Node, board: Board, alpha, beta, depth, ply, time_remaining=None, move_values=None):
        """
        Return the best value, best child of the current node. Also returns an
        updated move values dictionary. Agent specific.
        """
        return NotImplementedError
    