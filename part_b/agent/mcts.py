import numpy as np

from agent.board import Board
import copy
from agent.constants import WIN, LOSS, DRAW

board_legal_actions = dict()

class MCTSNode():
    def __init__(self, board: Board, color, parent=None, parent_action=None):
        self.state = board
        self.color = color
        self.parent = parent
        self.parent_action = parent_action
        self.children = dict()
        self._number_of_visits = 0
        self._results = {WIN: 0, LOSS: 0, DRAW: 0}
        self._untried_actions = self.state.get_legal_actions()
        self._legal_actions = self._untried_actions
        return
    
    def q(self):
        """
        Return the total utility of the current node, which is #wins
        """
        wins = self._results[WIN]
        return wins
    
    def n(self):
        """
        Return the total number of playouts through the current node
        """
        return self._number_of_visits
    
    def expand(self):
        """
        Expand the current node by adding to the tree a single new child of the
        current node
        """
        action = self._untried_actions.pop()
        next_board = copy.deepcopy(self.state)
        next_board.apply_action(action)
        child_node = MCTSNode(
            next_board, self.color, parent=self, parent_action=action)
        self.children[action] = child_node
        return child_node 
    
    def is_terminal_node(self):
        """
        Returns true if current board represented by the current node fulfils a
        winning condition.
        """
        return self.state.game_over
    
    def playout(self):
        current_playout_state = copy.deepcopy(self.state)
        player_possible_moves = self._legal_actions
        while not current_playout_state.game_over:
            action_info = self.playout_policy(current_playout_state, player_possible_moves)
            current_playout_state = action_info[1]
            player_possible_moves = action_info[2]
            # print("possible_moves", possible_moves)
            # print("action:", action)               
            # print("player:", current_playout_state._turn_color)
            # print("turn_count:", current_playout_state.turn_count)
            # print(current_playout_state.render(use_color=True))
        return current_playout_state.game_result(self.color)

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)
    
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0
    
    def choice_weight(self, c, c_param=1.414):
        return (c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n()))
    
    def best_child(self, c_param=1.414):
        choice_weights = []
        children = []
        for c in self.children.values():
            choice_weights.append(self.choice_weight(c, c_param))
            children.append(c)
        return children[np.argmax(choice_weights)]
    
    # ==========================================================================
    # Simulation Phase

    def playout_policy(self, state, possible_moves):
        return self.random_playout(state, possible_moves)
        # return self.heuristic_playout(state, possible_moves)
    
    def random_playout(self, state: Board, possible_moves):
        best_move = possible_moves[np.random.randint(len(possible_moves))]
        state.apply_action(best_move)
        return best_move, state, state.get_legal_actions()
    
    def heuristic_playout(self, state, possible_moves):
        utilities = []
        action_infos = []
        for move in possible_moves:
            action_info = self.eval_fn(state, move)
            utilities.append(action_info[0])
            action_infos.append(action_info)
        index = np.argmax(utilities)
        return action_infos[index]
    
    def eval_fn(self, state: Board, action):
        """
        Return the utility, board state and legal actions of the opponent for
        a given action
        """
        # board after applying the input action
        board = copy.deepcopy(state)
        board.apply_action(action)

        # calculate how many more legal actions can the player take compared
        # to the opponent
        opponent_actions = board.get_legal_actions()
        board.modify_turn_color()
        player_actions = board.get_legal_actions()
        board.modify_turn_color()
        num_opponent_actions = len(opponent_actions)
        num_player_actions = len(player_actions)
        num_extra_actions = num_player_actions - num_opponent_actions

        # calculate how many more tokens the player has compared to the opponent
        player_color = state._turn_color
        opponent_color = player_color.opponent
        num_player_tokens = board._player_token_count(player_color)
        num_opponent_tokens = board._player_token_count(opponent_color)
        num_extra_tokens = num_player_tokens - num_opponent_tokens

        utility = 0.5*num_extra_tokens + 0.5*num_extra_actions
        # print("num_extra_actions:", num_extra_actions, "num_extra_tokens:", num_extra_actions, "utility:", utility)
        return utility, board, opponent_actions
    # ==========================================================================
    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node
    
    def best_action(self):
        simulation_no = 20
        simulation_no += self.state.turn_count*2
        
        for i in range(simulation_no):
            v = self._tree_policy()
            reward = v.playout()
            v.backpropagate(reward)

            print("simulation no:", i, "game result:", reward)
        
        # sqrt(2)=1.414, this is the theoretical value of C
        return self.best_child(c_param=1.414)
    
    

