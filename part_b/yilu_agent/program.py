# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent
import random

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .board import Board, BOARD_N
from .habp import alpha_beta_cutoff_search, TranspositionTable

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
            legal_actions = self._board.get_legal_actions()
            return random.choice(legal_actions)

        # If the board is relatively full, play using alpha-beta pruning 
        print("Start the search")
        return alpha_beta_cutoff_search(self._board, self.transposition_table, referee)
    

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        # match self._color:
        #     case PlayerColor.RED:
        #         print("Testing: RED is playing a PLACE action")
        #         return PlaceAction(
        #             Coord(3, 3), 
        #             Coord(3, 4), 
        #             Coord(4, 3), 
        #             Coord(4, 2)
        #         )
        #     case PlayerColor.BLUE:
        #         print("Testing: BLUE is playing a PLACE action")
        #         return PlaceAction(
        #             Coord(2, 3), 
        #             Coord(2, 4), 
        #             Coord(2, 5), 
        #             Coord(2, 6)
        #         )
        


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Update state for {self._color}: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")

        self._board.apply_action(place_action)



