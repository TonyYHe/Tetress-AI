# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from habp_agent.habp import HABPNode
from utils.board import Board
import random
from utils.constants import *

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
        self.root = HABPNode(initial_board, color)
        self.next = None


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        num_empty_cells = len(self.root.state._empty_coords())
        if num_empty_cells > OPENING_STAGE:
        # if self.root.state._turn_count < OPENING_STAGE:
            legal_actions = self.root.state.get_legal_actions()
            best_action = random.choice(legal_actions)
        else:
            best_child = self.root.alpha_beta_cutoff_search()
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
                # this is more to do with mcts, because not all child nodes are 
                # generated in mcts
                if child_node is None:
                    self.root.state.apply_action(action)
                    self.root = HABPNode(self.root.state, self.root.color)
                else:
                    self.root = child_node
    