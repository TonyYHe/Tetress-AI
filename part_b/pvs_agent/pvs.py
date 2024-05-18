import numpy as np
from copy import deepcopy
import time

from utils.board import *
from utils.constants import *
from utils.table import *
from utils.node import *
from utils.tracktime import *


stateinfo_table = StateinfoTable()
transposition_table = TranspositionTable()
# ______________________________________________________________________________
class PVSNode(Node):
    def __init__(self, board: Board, color: PlayerColor, parent_action=None):
        super().__init__(board, color, parent_action)
        return
    
    def best_child(self, board: Board, time_remaining):
        """
        Return the best child node.
        """
        print("@ number of legal actions:", self.state_info.num_player_legal_actions)
        print("@ number of empty coordinates:", self.state_info.num_empty_cells)
        board = deepcopy(board)
        game_progress = self.state_info.num_player_legal_actions
        if board._turn_count == 0 or game_progress > MIDGAME_STAGE: 
            # play a safe random move
            print("%"*DELIM_LEN, "OPENING_GAME_STAGE", "%"*DELIM_LEN)
            best_child = self.get_safe_random_child(board)
        elif game_progress > LATEGAME_STAGE:
            # use principal variation search with random sampling and 
            # heuristic sorting in midgame stage
            print("%"*DELIM_LEN, "MIDGAME_STAGE", "%"*DELIM_LEN)
            allocated_time = MIDGAME_TIME + board._turn_count/TIME_OUT_FACTOR
            print("allocated time:", allocated_time)
            best_child = self.iterative_deepening_pvs(board, strategy=PVSNode.strategy, time_remaining=allocated_time)
        else:
            # complete principal variation search in endgame stage
            print("%"*DELIM_LEN, "LATEGAME_STAGE", "%"*DELIM_LEN)
            allocated_time = LATEGAME_TIME + board._turn_count/TIME_OUT_FACTOR
            print("allocated time:", allocated_time)
            best_child = self.iterative_deepening_pvs(board, strategy=PVSNode.strategy, time_remaining=allocated_time)
        return best_child

    @staticmethod
    def strategy(root, board: Board, ply: int, isMaximizingPlayer=True) -> list:
        """
        Return a list of children to investigate.
        """
        num_legal_actions = root.state_info.num_player_legal_actions if isMaximizingPlayer else root.state_info.num_opponent_legal_actions
        if num_legal_actions > LATEGAME_STAGE:
            n = min(num_legal_actions, SAMPLE_SIZE)
            # BRANCHING_FACTOR < SAMPLE_SIZE
            children = root.get_random_children(board, n, isMaximizingPlayer)[:BRANCHING_FACTOR]
        else:
            children = root.get_all_children(board, isMaximizingPlayer)
        key = Node.get_util_val(board, ply)
        sorted_children = sorted(children, key=key, reverse=isMaximizingPlayer)
        return sorted_children
    
    def get_all_children(self, board: Board, isMaximizingPlayer=True) -> list:
        """
        Return child nodes stored in dict[action, PVSNode].
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
            child_node = PVSNode(board, self.color, a)
            self.children[a] = child_node
            board.undo_action(mutation)
        return list(self.children.values())
    
    def get_random_children(self, board: Board, n: int, isMaximizingPlayer=True) -> list:
        legal_actions = self.state_info.player_legal_actions if isMaximizingPlayer else self.state_info.opponent_legal_actions
        random_actions = random.sample(legal_actions, n)
        random_children = []
        if self.children is None:
            self.children = dict()
        for a in random_actions:
            mutation = board.apply_action(a)
            child_node = self.children.get(a)
            if child_node is None:
                child_node = PVSNode(board, self.color, a)
                self.children[a] = child_node
            random_children.append(child_node)
            board.undo_action(mutation)
        return random_children

    def iterative_deepening_pvs(self, board: Board, strategy, time_remaining=None):
        start_time = time.time()
        depth = 1
        while depth < MAX_SEARCH_DEPTH:
            print("max depth:", depth)
            _, best_child = self.PVS_alpha_beta_search(board, -np.inf, np.inf, depth, 0, strategy, time_remaining)
            depth += 1
            time_remaining = time_left(time_remaining, start_time)
            if time_remaining is not None and time_remaining <= 0:
                break
        return best_child

    def PVS_alpha_beta_search(self, board: Board, alpha, beta, depth, ply, strategy, time_remaining=None):
        """
        Modified code from https://ics.uci.edu/~eppstein/180a/990202b.html
        Return the best child using Principle Variation Search. Utilises 
        transposition table to improve search efficiency.
        """
        if self.cutoff_test(depth):
            return self.state_info.eval_fn(board, self.color, ply), None
        
        entry: TTEntry = transposition_table.retrieve(board._state)
        if entry is not None and entry.depth >= depth:
            stored_score = entry.best_value
            if entry.node_type == EXACT:
                return stored_score, entry.best_child
            elif entry.node_type == LOWER_BOUND and stored_score > alpha:
                alpha = stored_score
            elif entry.node_type == UPPER_BOUND and stored_score < beta:
                beta = stored_score
            if alpha >= beta:
                return stored_score, entry.best_child
        
        start_time = time.time()
        best_value = -np.inf
        best_child = None
        
        children = strategy(self, board, ply, board._turn_color==self.color)
        pv_node = children[0]
        # num_legal_actions = self.state_info.num_player_legal_actions if board._turn_color==self.color else self.state_info.num_opponent_legal_actions
        # print("depth:", depth, "total number of children:", num_legal_actions)
        # print("top k:", len(children))

        for child_node in children:
            # print("color:", board._turn_color, "depth:", depth, "before applying action:", child_node.parent_action)
            # print(board.render(use_color=True))
            mutation = board.apply_action(child_node.parent_action)
            # print("color:", board._turn_color, "depth:", depth, "after applying action:", child_node.parent_action)
            # print(board.render(use_color=True))
            if pv_node == child_node:
                value = -child_node.PVS_alpha_beta_search(board, -beta, -alpha, depth - 1, ply + 1, strategy, time_remaining)[0]
            else:
                value = -child_node.PVS_alpha_beta_search(board, -alpha-1, -alpha, depth - 1, ply + 1, strategy, time_remaining)[0]
                if alpha < value and value < beta:
                    value = -child_node.PVS_alpha_beta_search(board, -beta, -value, depth - 1, ply + 1, strategy, time_remaining)[0]
            board.undo_action(mutation)
            # print("color:", board._turn_color, "depth:", depth, "after reversing action:", child_node.parent_action)
            # print(board.render(use_color=True))
            if value > best_value:
                best_value = value
                if value > alpha:
                    alpha = value
                    best_child = child_node
                    if alpha >= beta:
                        break       
            time_remaining = time_left(time_remaining, start_time)     
            if time_remaining is not None and time_remaining <= 0:
                break
        
        node_type = EXACT
        if best_value <= alpha:
            node_type = UPPER_BOUND
        elif best_value >= beta:
            node_type = LOWER_BOUND

        transposition_table.store(board, node_type, depth, best_child, best_value, self.state_info)

        return best_value, best_child











        


    




    
