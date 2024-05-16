from utils.board import *
from utils.constants import *

class StateInformation:
    def __init__(self, board: Board, player_color: PlayerColor):
        # compute legal actions of the player and the opponent
        curr_color = board._turn_color
        board.modify_turn_color(player_color)
        self.player_legal_actions = board.get_legal_actions()
        self.num_player_legal_actions = len(self.player_legal_actions)
        board.modify_turn_color(player_color.opponent)
        self.opponent_legal_actions = board.get_legal_actions()
        self.num_opponent_legal_actions = len(self.opponent_legal_actions)
        board.modify_turn_color(curr_color)

        # compute other statistics
        self.num_empty_cells = len(board._empty_coords())
        self.num_player_token_count = len(board._player_occupied_coords(player_color))
        self.num_opponent_token_count = len(board._player_occupied_coords(player_color.opponent))
        self.game_over = board.game_over
        self.game_result = None
        if self.game_over:
            self.game_result = board.game_result(player_color)

    # def eval_fn(self, board: Board, player_color: PlayerColor, depth: int):
    #     """
    #     Return a utility value calculated from the persepctive of the player, 
    #     given a board. 
    #     """
    #     curr_color = board._turn_color
    #     if self.game_over == True:
    #         return self.game_result * 1000 - self.game_result * depth

    #     # Find the difference in the number of actions 
    #     utility = self.diff_legal_actions()

    #     # since Tetress is a zero-sum game, we can take the negative of the 
    #     # utility value for the opponent
    #     return utility if player_color != curr_color else -utility
    
    def eval_fn(self, board: Board, player_color: PlayerColor, depth: int):
        """
        Return a utility value calculated from the persepctive of the player, 
        given a board. 
        """
        curr_color = board._turn_color
        if self.game_over == True:
            return self.game_result * 1000 - self.game_result * depth

        # Find the difference in the number of actions 
        extra_num_actions = self.diff_legal_actions()
        # Find the difference in the number of cells occupied 
        extra_num_occupied = self.diff_cells_occupied()

        if board._turn_count < TURN_THRESHOLD: 
            # Far away from turns limitation 
            utility = extra_num_actions + extra_num_occupied * 0.1 
        else: 
            # If about to reach turns limit, evalution also include the number of cells occupied 
            turns_exceed_threshold = board._turn_count - TURN_THRESHOLD
            utility = extra_num_actions + extra_num_occupied * turns_exceed_threshold * 0.5 

        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if player_color != curr_color else -utility
    
    def eval_fn_token_count(self):
        return self.diff_cells_occupied()
    
    def eval_fn_num_legal_actions(self):
        return self.diff_legal_actions()
    
    def diff_cells_occupied(self) -> int:
        """
        Find the difference in the number of tokens between the player and the 
        opponent. 
        """
        return self.num_player_token_count - self.num_opponent_token_count


    def diff_legal_actions(self) -> int: 
        """
        Find the difference in the number of legal actions between the player and 
        the opponent. 
        """
        return self.num_player_legal_actions - self.num_opponent_legal_actions