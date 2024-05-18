from utils.board import *
from copy import deepcopy
from utils.constants import *
import random
from utils.table import *
import time

# ______________________________________________________________________________
class Node():
    def __init__(self, board: Board, color: PlayerColor, stateinfo_table: StateinfoTable, parent_action=None):
        self.color = color
        self.parent_action = parent_action
        self.children = None
        self.ordered_children = None
        self.state_info: StateInformation = stateinfo_table.retrieve(board._state)
        if self.state_info is None:
            self.state_info = stateinfo_table.store(board, color)
        return
    
    @staticmethod
    def get_util_val(board: Board, ply: int):
        def key(node: Node):
            mutation = board.apply_action(node.parent_action)
            util_val = node.state_info.eval_fn(board, node.color, ply)
            board.undo_action(mutation)
            return util_val
        return key
    
    def cutoff_test(self, depth):
        return depth == 0 or self.state_info.game_over
    
    # @staticmethod
    # def strategy(self, board: Board, ply: int, isMaximizingPlayer=True) -> list:
    #     """
    #     Return a list of children to investigate.
    #     """
    #     num_legal_actions = self.state_info.num_player_legal_actions if isMaximizingPlayer else self.state_info.num_opponent_legal_actions
    #     if num_legal_actions > LATEGAME_STAGE:
    #         n = min(num_legal_actions, SAMPLE_SIZE)
    #         # BRANCHING_FACTOR < SAMPLE_SIZE
    #         children = self.get_random_children(board, n, isMaximizingPlayer)[:BRANCHING_FACTOR]
    #     else:
    #         children = self.get_all_children(board, isMaximizingPlayer)
    #     key = Node.get_util_val(board, ply)
    #     sorted_children = sorted(children, key=key, reverse=isMaximizingPlayer)
    #     return sorted_children
    
    @staticmethod
    def reorder_children(board: Board, children: list, move_values):
        if move_values == {}:
            return children
        def get_move_value(node: Node):
            mutation = board.apply_action(node.parent_action)
            value = move_values.get(board._state.__hash__())
            board.undo_action(mutation)
            if value is None:
                return 0
            return value

        children.sort(key=get_move_value, reverse=True)
        return children
    
    def get_safe_random_child(self,board: Board, stateinfo_table: StateinfoTable):
        """
        Return a random child that makes a safe move. A safe move is defined as
        take an action that increases the number of legal actions.
        """
        safe = False
        start_time = time.time()
        while not safe and time.time() - start_time < SAFE_RANDOM_TIME_OUT:
            random_action = random.choice(self.state_info.player_legal_actions)
            mutation = board.apply_action(random_action)
            random_child = Node(board, self.color, stateinfo_table, parent_action=random_action)
            board.undo_action(mutation)
            safe = random_child.state_info.num_player_legal_actions > self.state_info.num_player_legal_actions

        return random_child
    
    def sort_all_children(self, board: Board, ply: int, stateinfo_table: StateinfoTable, isMaximizingPlayer=True) -> list:
        """
        Return sorted child nodes. Sort child nodes based on utility value. 
        Sorts in descending order if current node is MAX, otherwise sort in 
        ascending order.
        """
        # Check if children has been sorted already
        if self.ordered_children is not None:
            return self.ordered_children
        self.get_all_children(board, stateinfo_table, isMaximizingPlayer)
        key = Node.get_util_val(board, ply)
        self.ordered_children = sorted(self.children.values(), key=key, reverse=isMaximizingPlayer)
        return self.ordered_children
    
    def get_all_children(self, board: Board, stateinfo_table: StateinfoTable, isMaximizingPlayer=True) -> list:
        """
        """
        # Check if children has been generated already
        legal_actions = self.state_info.player_legal_actions if isMaximizingPlayer else self.state_info.opponent_legal_actions
        num_legal_actions = self.state_info.num_player_legal_actions if isMaximizingPlayer else self.state_info.num_opponent_legal_actions

        if self.children is not None and len(self.children) == num_legal_actions:
            return list(self.children.values())
        if self.children is None:
            self.children = dict()

        remaining_legal_actions = list(set(legal_actions) - set(self.children.keys()))
        for a in remaining_legal_actions:
            mutation = board.apply_action(a)
            child_node = Node(board, self.color, stateinfo_table, a)
            self.children[a] = child_node
            board.undo_action(mutation)
        return list(self.children.values())
    
    def get_random_children(self, board: Board, n: int, stateinfo_table: StateinfoTable, isMaximizingPlayer=True) -> list:
        legal_actions = self.state_info.player_legal_actions if isMaximizingPlayer else self.state_info.opponent_legal_actions
        random_actions = random.sample(legal_actions, n)
        random_children = []

        if self.children is None:
            self.children = dict()

        for a in random_actions:
            mutation = board.apply_action(a)
            child_node = self.children.get(a)
            if child_node is None:
                child_node = Node(board, self.color, stateinfo_table, a)
                self.children[a] = child_node
            random_children.append(child_node)
            board.undo_action(mutation)
        return random_children
    













        


    




    
