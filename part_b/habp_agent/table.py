from utils.board import *
from utils.constants import *
from habp_agent.stateinfo import StateInformation

class Table:
    def __init__(self):
        self.table = dict()

    def retrieve(self, boardstate: BoardState):
        state_hash = boardstate.hash()
        return self.table.get(state_hash)

class StateinfoTable(Table):
    def __init__(self):
        super().__init__()

    def store(self, board: Board, player_color: PlayerColor):
        boardstate = board._state
        state_hash = boardstate.hash()
        state_info = StateInformation(board, player_color)
        self.table[state_hash] = state_info
        return self.table[state_hash]

class TranspositionTable(Table):
    def __init__(self):
        super().__init__()
        
    def store(self, board: Board, node_type, depth, best_child, state_info: StateInformation):
        boardstate = board._state
        state_hash = boardstate.hash()
        self.table[state_hash] = TTEntry(node_type, depth, best_child, state_info)
        return self.table[state_hash]
    
class TTEntry:
    def __init__(self, node_type, depth, best_child, state_info: StateInformation):
        self.node_type = node_type
        self.depth = depth
        self.best_child = best_child
        self.state_info = state_info

