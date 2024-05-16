import numpy as np

from utils.board import *
from copy import deepcopy
from utils.constants import *
import random
from utils.table import *
import time

stateinfo_table = StateinfoTable()
transposition_table = TranspositionTable()
# ______________________________________________________________________________
class HABPNode():
    def __init__(self, board: Board, color: PlayerColor, parent_action=None):
        self.color = color
        self.parent_action = parent_action
        self.children = None
        self.ordered_children = None
        self.state_info = stateinfo_table.retrieve(board._state)
        if self.state_info is None:
            self.state_info = stateinfo_table.store(board, color)
        return
    
    @staticmethod
    def get_util_val(board: Board, depth: int):
        board: Board = board
        depth: int = depth
        def key(node: HABPNode):
            mutation = board.apply_action(node.parent_action)
            util_val = node.state_info.eval_fn(board, node.color, depth)
            board.undo_action(mutation)
            return util_val
        return key
    
    def sort_children(self, board: Board, depth: int, isMaximizingPlayer=True) -> list:
        """
        Return sorted child nodes. Sort child nodes based on utility value. 
        Sorts in descending order if current node is MAX, otherwise sort in 
        ascending order.
        """
        # Check if children has been sorted already
        if self.ordered_children is not None:
            return self.ordered_children
        
        key = HABPNode.get_util_val(board, depth)
        
        self.ordered_children = sorted(self.children.values(), key=key, reverse=isMaximizingPlayer)
        return self.ordered_children
        
    def get_children(self, board: Board, isMaximizingPlayer=True) -> dict:
        """
        Return child nodes stored in dict[action, HABPNode].
        """
        # Check if children has been generated already
        if self.children is not None:
            return self.children
        
        legal_actions = self.state_info.player_legal_actions if isMaximizingPlayer else self.state_info.opponent_legal_actions
        self.children = dict()
        for a in legal_actions:
            mutation = board.apply_action(a)
            child_node = HABPNode(board, self.color, a)
            self.children[a] = child_node
            board.undo_action(mutation)
        return self.children
    
    def get_safe_random_child(self, board: Board):
        """
        Return a random child that makes a safe move. A safe move is defined as
        take an action that increases the number of legal actions.
        """
        safe = False
        start_time = time.time()
        while not safe and time.time() - start_time < SAFE_RANDOM_TIME_OUT:
            random_action = random.choice(self.state_info.player_legal_actions)
            mutation = board.apply_action(random_action)
            random_child = HABPNode(board, self.color, parent_action=random_action)
            board.undo_action(mutation)
            safe = random_child.state_info.num_player_legal_actions > self.state_info.num_player_legal_actions

        return random_child
        
    def cutoff_test(self, depth):
        return depth == 0 or self.state_info.game_over












        


    




    
