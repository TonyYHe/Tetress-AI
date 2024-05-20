# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent
import random

from referee.game import PlayerColor, Action, PlaceAction
from .board import Board, BOARD_N
from .habp import iterative_deepening_alpha_beta_cutoff_search, TranspositionTable, row_col_occupied
import time

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
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")
        
        self._board = Board()
        self.transposition_table = TranspositionTable(color)

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        # If the board is relatively empty, play randomly  
        EMPTY_THRESHOLD = BOARD_N * BOARD_N * 3 / 5
        if len(self._board._empty_coords()) > EMPTY_THRESHOLD: 
            # Generate a random action 
            legal_actions = self._board.get_legal_actions()
            action = random.choice(legal_actions)
            num_row_col_occupied = row_col_occupied(self._board, self._color)

            # Check for safety
            cutoff_time = time.time() + 0.5
            while (time.time() < cutoff_time): 
                self._board.apply_action(action)
                #new_legal_actions = self._board.get_legal_actions()
                new_num_row_col_occupied = row_col_occupied(self._board, self._color)
                self._board.undo_action()
                if (num_row_col_occupied > new_num_row_col_occupied): 
                    return action
                action = random.choice(legal_actions)

            return action 

        # If the board is relatively full, play using alpha-beta pruning 
        return iterative_deepening_alpha_beta_cutoff_search(self._board, self.transposition_table, referee)


    def update(self, color: PlayerColor, action: PlaceAction, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self._board.apply_action(action)



