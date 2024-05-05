import numpy as np
from collections import defaultdict

from agent.board import Board
import copy

class MCTSNode():
    def __init__(self, board: Board, parent=None, parent_action=None):
        self.state = board
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        self._legal_actions = self._untried_actions
        return
    
    def untried_actions(self):
        self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions
    
    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses
    
    def n(self):
        return self._number_of_visits
    
    def expand(self):
        action = self._untried_actions.pop()
        next_board = copy.deepcopy(self.state)
        next_board.apply_action(action)
        child_node = MCTSNode(
            next_board, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node 
    
    def is_terminal_node(self):
        return self.state.game_over
    
    def rollout(self):
        current_rollout_state = copy.deepcopy(self.state)
        possible_moves = self._legal_actions
        while not current_rollout_state.game_over:
            action = self.rollout_policy(possible_moves)
            current_rollout_state.apply_action(action)
            possible_moves = current_rollout_state.get_legal_actions()

            # print("possible_moves", possible_moves)
            # print("action:", action)               
            # print("player:", current_rollout_state._turn_color)
            # print("turn_count:", current_rollout_state.turn_count)
            # print(current_rollout_state.render(use_color=True))
        
        return current_rollout_state.game_result             

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)
    
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0
    
    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]
    
    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]
    
    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node
    
    def best_action(self):
        simulation_no = 30
        
        for i in range(simulation_no):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)

            print("simulation no:", i, "game result:", reward)
        
        # sqrt(2)=1.414, this is the theoretical value of C
        return self.best_child(c_param=1.414)
    

