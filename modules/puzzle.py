import logging

from modules.position_list_node import PositionListNode
from modules.puzzle_pgn import PuzzlePgn
from modules.bcolors import bcolors

# minimum number of moves required for a puzzle to be considered complete
MIN_MOVES = 3

class Puzzle(object):
    """ last_pos = chess.Board instance
    """
    def __init__(self, last_pos, last_move, game_id, info_handler, game, strict):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game_id = game_id
        last_pos.push(last_move)
        self.position_list_node = PositionListNode(last_pos, info_handler, strict)
        self.game = game

    def to_pgn(self):
        return PuzzlePgn(self).export()

    def color(self):
        return self.position_list_node.position.turn

    def is_complete(self):
        if self.position_list_node.ambiguous():
            return False
        if len(self.position_list_node.move_list()) < MIN_MOVES:
            return False
        return self.position_list_node.is_complete(
            self.position_list_node.category(),
            self.color(),
            True,
            self.position_list_node.material_difference()
        )

    def generate(self, depth):
        self.position_list_node.generate(depth)
        if self.is_complete():
            logging.debug(bcolors.OKGREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.FAIL + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.position_list_node.category()
