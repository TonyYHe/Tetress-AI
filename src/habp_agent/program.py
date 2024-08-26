# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from utils.board import Board
from utils.constants import *
from habp_agent.habp_agent import *
from utils.node import *

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
        self.agent = NegamaxAgent(color)


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        print("@ starting time:", referee["time_remaining"])
        print("@ starting space:", referee["space_remaining"])
        print("turn count:", self.board.turn_count)
        best_action = self.agent.best_action(self.board, referee["time_remaining"])
        print("@ ending time:", referee["time_remaining"])
        print("@ ending space:", referee["space_remaining"])
        return best_action
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board.apply_action(action)
