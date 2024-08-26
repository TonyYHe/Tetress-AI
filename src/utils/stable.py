from utils.board import *
from utils.constants import *
from utils.orderactions import *
from utils.ttable import *
    
class StateinfoTable(Table):
    def __init__(self):
        super().__init__()

    def store(self, board: Board, depth, ttable: TranspositionTable, move_values):
        state_hash = board._state.__hash__()
        player_color = board._turn_color
        player_actions = board.get_legal_actions()
        board.modify_turn_color(player_color.opponent)
        opponent_actions = board.get_legal_actions()
        board.modify_turn_color(player_color)
        ordered_player_actions = OrderActions.order_actions(board, player_actions, ttable, move_values)
        ordered_opponent_actions = OrderActions.order_actions(board, opponent_actions, ttable, move_values)
        state_info = {player_color: ordered_player_actions[:TOPK], player_color.opponent: ordered_opponent_actions[:TOPK], "depth": depth}
        self.table[state_hash] = state_info
        return state_info
    
    def retrieve(self, board: Board, depth, ttable: TranspositionTable, move_values):
        state_info = super().retrieve(board._state)
        if state_info is None:
            state_info = self.store(board, depth, ttable, move_values)
        if state_info["depth"] >= depth:
            return state_info
        else:
            state_info = self.store(board, depth, ttable, move_values)
            return state_info

