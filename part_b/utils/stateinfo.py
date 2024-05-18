from utils.board import *
from utils.constants import *

class StateInformation:
    def __init__(self, board: Board):
        # compute legal actions of the player and the opponent
        self.curr_color = board._turn_color
        self.player_legal_actions = board.get_legal_actions()
        self.num_player_legal_actions = len(self.player_legal_actions)
        board.modify_turn_color(self.curr_color.opponent)
        self.opponent_legal_actions = board.get_legal_actions()
        self.num_opponent_legal_actions = len(self.opponent_legal_actions)
        board.modify_turn_color(self.curr_color)

        # compute other statistics
        self.num_empty_cells = len(board._empty_coords())
        self.num_player_token_count = len(board._player_occupied_coords(self.curr_color))
        self.num_opponent_token_count = len(board._player_occupied_coords(self.curr_color.opponent))
        self.winner_color = board.winner_color
    
    def eval_fn(self, player_color: PlayerColor, ply: int):
        # player color should always be THE PLAYER (YOU)
        """
        problematic
        Return a utility value calculated from the persepctive of the input 
        player, given a board. 
        """
        if self.winner_color is not None:
            if self.winner_color == player_color:
                return 1000 - ply
            else:
                return -1000 + ply

        # Find the difference in the number of actions 
        utility = self.diff_legal_actions()

        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return -utility if player_color != self.curr_color else utility
    
    
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