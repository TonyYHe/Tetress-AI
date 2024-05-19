# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import *
from utils.board import Board
from utils.habp import HABPNode


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


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        action_utility = []
        for action in self.board.get_legal_actions():
            mutation = self.board.apply_action(action)
            num_player_token_count = self.board._player_token_count(self.color)
            num_opponent_token_count = self.board._player_token_count(self.color.opponent)
            utility_value = num_player_token_count - num_opponent_token_count
            self.board.undo_action(mutation)
            action_utility.append((action, utility_value))
        sorted_children = sorted(action_utility, key=lambda x: x[1])
        return sorted_children[0][0]
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board.apply_action(action)
    