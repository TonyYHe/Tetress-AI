# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from utils.board import Board
from copy import deepcopy
from utils.eval_fn import *

transposition_table = dict()

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
        legal_actions = self.board.get_legal_actions()
        action_utility = []
        for action in legal_actions:
            new_board = deepcopy(self.board)
            new_board.apply_action(action)
            is_game_over = new_board.game_over
            utility = eval_fn(self.board, self.color, transposition_table, game_over=is_game_over)
            action_utility.append((action, utility))

        action_utility.sort(key=lambda x: x[1])
        print("#legal actions:", len(legal_actions))
        return action_utility[-1][0]
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board.apply_action(action)
    