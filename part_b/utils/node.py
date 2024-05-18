from utils.board import *
from copy import deepcopy
from utils.constants import *
import random
from utils.table import *
import time

# ______________________________________________________________________________
class Node:
    def __init__(self, board: Board, parent_action=None):
        self.parent_action = parent_action
        self.children = None
        self.state_info: StateInformation = StateInformation(board)
        return
    
    def cutoff_test(self, depth):
        return depth == 0 or (self.state_info.winner_color is not None)
    
    def get_safe_random_child(self,board: Board):
        """
        Return a random child that makes a safe move. A safe move is defined as
        take an action that increases the number of legal actions.
        """
        safe = False
        start_time = time.time()
        while not safe and time.time() - start_time < SAFE_RANDOM_TIME_OUT:
            random_action = random.choice(self.state_info.player_legal_actions)
            mutation = board.apply_action(random_action)
            random_child = Node(board, parent_action=random_action)
            board.undo_action(mutation)
            safe = random_child.state_info.num_player_legal_actions > self.state_info.num_player_legal_actions

        return random_child
    
    def get_all_children(self, board: Board) -> list:
        # Check if children has been generated already
        legal_actions = self.state_info.player_legal_actions
        num_legal_actions = self.state_info.num_player_legal_actions

        if self.children is not None and len(self.children) == num_legal_actions:
            return list(self.children.values())
        if self.children is None:
            self.children = dict()

        remaining_legal_actions = list(set(legal_actions) - set(self.children.keys()))
        for a in remaining_legal_actions:
            mutation = board.apply_action(a)
            child_node = Node(board, a)
            self.children[a] = child_node
            board.undo_action(mutation)
        return list(self.children.values())
    
    def get_random_children(self, board: Board, n: int) -> list:
        legal_actions = self.state_info.player_legal_actions
        random_actions = random.sample(legal_actions, n)
        random_children = []

        if self.children is None:
            self.children = dict()

        for a in random_actions:
            mutation = board.apply_action(a)
            child_node = self.children.get(a)
            if child_node is None:
                child_node = Node(board, a)
                self.children[a] = child_node
            random_children.append(child_node)
            board.undo_action(mutation)
        return random_children
    












        


    




    
