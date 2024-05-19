# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from utils.board import Board
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
        self.board = Board(initial_player=PlayerColor.RED)


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        legal_actions = self.board.get_legal_actions()
        return random.choice(legal_actions)
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board.apply_action(action)



