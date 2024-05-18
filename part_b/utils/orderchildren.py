from utils.node import *
from utils.table import *

class OrderChildren:
    @staticmethod
    def order_children(board: Board, children: list, player_color: PlayerColor, ttable: TranspositionTable, move_values):
        move_scores = {}
        ordered_children = []

        for child_node in children:
            mutation = board.apply_action(child_node.parent_action)
            ttentry: TTEntry = ttable.retrieve(board._state)
            if ttentry is not None:
                move_scores[board._state] = ttentry.best_value
            else:
                if board._state in move_values:
                    move_scores[board._state] = move_values[board._state]
                else:
                    move_scores[board._state] = OrderChildren.heuristic_evaluate_child(child_node, player_color)
            board.undo_action(mutation)

        def get_move_score(node: Node):
            mutation = board.apply_action(child_node.parent_action)
            value = move_scores[board._state]
            board.undo_action(mutation)
            return value

        ordered_children = sorted(children, key=get_move_score)
        return ordered_children
    
    @staticmethod
    def heuristic_evaluate_child(node: Node, player_color: PlayerColor):
        heuristic_value = node.state_info.diff_cells_occupied() + node.state_info.diff_legal_actions()
        if player_color == node.state_info.curr_color:
            return heuristic_value
        return -heuristic_value

        
