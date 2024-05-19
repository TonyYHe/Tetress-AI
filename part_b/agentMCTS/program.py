# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# =============================================================================
# BROKEN DO NOT USE!
# =============================================================================

from referee.game import PlayerColor, Action, PlaceAction, Coord
from agentMCTS.mcts import MCTSNode
from utils.board import Board
from utils.constants import *
import random


class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        initial_board = Board(initial_player=PlayerColor.RED)
        self.root = MCTSNode(initial_board, color)
        self.next = None

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        num_empty_cells = len(self.root.state._empty_coords())
        if num_empty_cells > OPENING_STAGE:
            legal_actions = self.root.state.get_legal_actions()
            best_action = random.choice(legal_actions)
        else:
            best_child = self.root.best_action()
            self.next = best_child
            best_action = best_child.parent_action
        return best_action
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        num_empty_cells = len(self.root.state._empty_coords())
        if num_empty_cells > OPENING_STAGE:
            self.root.state.apply_action(action)
        else:
            if color == self.root.color:
                self.root = self.next
            else:
                child_node = self.root.children.get(action)
                if child_node is None:
                    self.root.state.apply_action(action)
                    self.root = MCTSNode(self.root.state, self.root.color)
                else:
                    self.root = child_node

        # print("initial color:", initial_color, "| initial turn_count:", initial_turn_count)
        # print("input color:", color, "| input action:", action)
        # print("current color:", self.root.state.turn_color, "| turn_count:", self.root.state.turn_count)
        # print(self.root.state.render(use_color=True))