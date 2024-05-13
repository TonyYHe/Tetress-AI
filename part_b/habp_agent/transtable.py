from utils.board import *
from utils.constants import *
from habp_agent.stateinfo import StateInformation

class TranspositionTable:
    def __init__(self):
        self.table = dict()
        
    def store(self, board: Board, player_color: PlayerColor):
        boardstate = board._state
        state_hash = boardstate.hash()
        self.table[state_hash] = StateInformation(board, player_color)
        return self.table[state_hash]
                                 
    def retrieve(self, boardstate: BoardState) -> StateInformation:
        state_hash = boardstate.hash()
        return self.table.get(state_hash)