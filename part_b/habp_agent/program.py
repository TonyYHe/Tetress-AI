# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from habp_agent.habp import HABPNode
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
        initial_board = Board(initial_player=PlayerColor.RED)
        self.root = HABPNode(initial_board, color)
        self.next = None


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        best_child = self.root.alpha_beta_cutoff_search()
        self.next = best_child
        return best_child.parent_action
       

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        # initial_color = self.board.turn_color
        # initial_turn_count = self.board.turn_count

        if color == self.root.color:
            self.root = self.next
        else:
            child_node = self.root.children.get(action)
            if child_node is None:
                self.root.state.apply_action(action)
                self.root = HABPNode(self.root.state, self.root.color)
            else:
                self.root = child_node

        # print("initial color:", initial_color, "| initial turn_count:", initial_turn_count)
        # print("input color:", color, "| input action:", action)
        # print("current color:", self.board.turn_color, "| turn_count:", self.board.turn_count)
        # print(self.board.render(use_color=True))
    