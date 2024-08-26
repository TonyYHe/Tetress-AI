import numpy as np

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.iterdeep_agent import *
from utils.orderactions import *
from utils.searchexit import *

# ______________________________________________________________________________
class NegamaxAgent(IterativeDeepeningAgent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)
        return

    def search(self, board: Board, alpha, beta, depth, ply, move_values):
        return self.alpha_beta_with_memory(board, alpha, beta, depth, ply, move_values)









        


    




    
