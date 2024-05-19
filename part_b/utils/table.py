from utils.board import *
from utils.constants import *
from utils.stateinfo import StateInformation

class Table:
    def __init__(self):
        self.table = dict()

    def retrieve(self, boardstate: BoardState):
        state_hash = boardstate.__hash__()
        return self.table.get(state_hash)
    
class StateinfoTable(Table):
    def __init__(self):
        super().__init__()

    def store(self, board: Board):
        boardstate = board._state
        state_hash = boardstate.__hash__()
        state_info = StateInformation(board)
        self.table[state_hash] = state_info
        return state_info
    
    def retrieve(self, board: Board):
        state_info = super().retrieve(board._state)
        if state_info is None:
            state_info = self.store(board)
        return state_info

class TranspositionTable(Table):
    def __init__(self):
        super().__init__()
        
    def store(self, board: Board, node_type, depth, best_action, best_value):
        state_hash = board._state.__hash__()
        entry = TTEntry(node_type, depth, best_action, best_value)
        self.table[state_hash] = entry
        return entry
    
    def remove_least_valuable_entry(self):
        least_valuable_key = min(self.table, key=lambda x: self.table[x].depth)
        del self.table[least_valuable_key]
    
class TTEntry:
    def __init__(self, node_type, depth, best_action, best_value):
        self.node_type = node_type
        self.depth = depth
        self.best_action = best_action
        self.best_value = best_value

