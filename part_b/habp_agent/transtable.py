from utils.board import  BoardState
from utils.constants import *

class TranspositionTable:
    def __init__(self):
        self.table = dict()
        
    def store(self, boardstate: BoardState, value: int):
        state_hash = boardstate.hash()
        self.table[state_hash] = value
                                 
    def retrieve(self, boardstate: BoardState):
        state_hash = boardstate.hash()
        return self.table.get(state_hash)