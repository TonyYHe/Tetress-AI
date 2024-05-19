from utils.node import *
from utils.table import *

class OrderChildren:
    @staticmethod
    def order_children(board: Board, children: list, player_color: PlayerColor, ttable: TranspositionTable):
        """
        Return a sorted list of children based on best value stored in 
        transposition table, best value from previous iteration and heuristic 
        value.
        """
        move_scores = {}
        ordered_children = []

        for child_node in children:
            mutation = board.apply_action(child_node.parent_action)
            ttentry: TTEntry = ttable.retrieve(board._state)
            if ttentry is not None:
                move_scores[board._state.__hash__()] = ttentry.best_value
            else:
                move_scores[board._state.__hash__()] = OrderChildren.heuristic_evaluate_child(child_node, player_color)
            board.undo_action(mutation)

        def get_move_score(node: Node):
            mutation = board.apply_action(child_node.parent_action)
            value = move_scores[board._state.__hash__()]
            board.undo_action(mutation)
            return value

        ordered_children = sorted(children, key=get_move_score, reverse=True)
        return ordered_children
    
    @staticmethod
    def topk_children(children):
        """
        Return the top k children of the input list of child nodes.
        """
        k = min(len(children), 20)
        return children[:k]
    
    @staticmethod
    def heuristic_evaluate_child(node: Node, player_color: PlayerColor):
        """
        Return the heuristic value of a node evaluated from the perspective of 
        the input player.
        """
        heuristic_value = node.state_info.diff_cells_occupied() + node.state_info.diff_legal_actions()
        if player_color == node.state_info.curr_color:
            return heuristic_value
        return -heuristic_value

        
