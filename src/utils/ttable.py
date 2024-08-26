from utils.board import *
from utils.constants import *
from utils.table import *

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
