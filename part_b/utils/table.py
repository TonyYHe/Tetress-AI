from utils.board import *
from utils.constants import *

class Table:
    def __init__(self):
        self.table = dict()

    def retrieve(self, boardstate: BoardState):
        state_hash = boardstate.__hash__()
        return self.table.get(state_hash)

class TranspositionTable(Table):
    def __init__(self):
        super().__init__()
        
    def store(self, board: Board, node_type, depth, best_child, best_value):
        boardstate = board._state
        state_hash = boardstate.__hash__()
        entry = TTEntry(node_type, depth, best_child, best_value)
        self.table[state_hash] = entry
        return entry
    
class TTEntry:
    def __init__(self, node_type, depth, best_child, best_value):
        self.node_type = node_type
        self.depth = depth
        self.best_child = best_child
        self.best_value = best_value

