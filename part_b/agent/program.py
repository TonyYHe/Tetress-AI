# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from agent.mcts import MCTSNode
from agent.board import Board


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
        initial_board = Board(initial_player=color)
        print("player color:", color)
        self.root = MCTSNode(initial_board)


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        best_child = self.root.best_action()
        return best_child.parent_action
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.root.state.update(action, color)
        self.root = MCTSNode(self.root.state)

        # initial_color = self.root.state.turn_color
        # initial_turn_count = self.root.state.turn_count
        # print("initial color:", initial_color, "initial turn_count:", initial_turn_count)
        # print("input color:", color, "input action:", action)
        # print("current color:", self.root.state.turn_color, "turn_count:", self.root.state.turn_count)
        # print(self.root.state.render(use_color=True))
    
