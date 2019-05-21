import logging

from modules.bcolors import bcolors
from modules.utils import fullmove_string


def log_board(board):
    """ Logs the fen string and board representation
    """
    logging.debug(bcolors.BLUE + board.fen())
    logging.debug(bcolors.YELLOW + str(board) + bcolors.ENDC)

def log_move(board, move, score, show_uci=False, highlight=False):
    """ 23. Qe4     CP: 123
    """
    move_str = "%s%s" % (fullmove_string(board), board.san(move))
    log_str = bcolors.GREEN
    if show_uci:
        log_str += ("  %s (%s)" % (move_str, move.uci())).ljust(22)
    else:
        log_str += "  %s" % move_str.ljust(15)
    log_str += bcolors.BLUE
    if score.is_mate():
        log_str += ("   Mate: %d" % score.mate()).ljust(12)
    else:
        log_str += ("   CP: %d" % score.score()).ljust(12)
    if highlight:
        log_str += bcolors.YELLOW + "   Investigate!"
    logging.debug(log_str + bcolors.ENDC)

