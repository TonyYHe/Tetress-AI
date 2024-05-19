# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from agentPVS.pvs_agent import PVSNode
from utils.board import Board
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
        self.board = Board(initial_player=PlayerColor.RED)
        self.color = color
        self.root = PVSNode(self.board, color)
        self.best_child = None


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        print("@ starting time:", referee["time_remaining"])
        print("@ starting space:", referee["space_remaining"])
        best_child = self.root.best_child(self.board, referee["time_remaining"])
        self.best_child = best_child
        best_action = best_child.parent_action
        print("@ ending time:", referee["time_remaining"])
        print("@ ending space:", referee["space_remaining"])
        return best_action
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board.apply_action(action)

        # update the root node of the habp search tree
        if color == self.color:
            self.root = self.best_child
        else:
            child_node: PVSNode = self.root.children.get(action) if self.root.children is not None else None
            # some child nodes may not be generated due to approximation
            if child_node is None:
                self.root = PVSNode(self.board, self.color, parent_action=action)
            else:
                self.root = child_node
