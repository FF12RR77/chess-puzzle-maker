import chess
import chess.uci

def sign(score):
    s = score.cp or score.mate
    if s > 0:
        return 1
    elif s < 0:
        return -1
    return 0

def material_total(board):
    return sum(v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_difference(board):
    return sum(v * (len(board.pieces(pt, True)) - len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_count(board):
    return chess.popcount(board.occupied)

def fullmove_string(board):
    move_str = str(board.fullmove_number)
    if board.turn:
        move_str = "%s.   " % move_str
    else:
        move_str = "%s... " % move_str
    return move_str

def normalize_score(board, score):
    """ flip the signs of the score to be from white's perspective
    """
    polarity = 1 if board.turn else -1
    if score.mate:
        return chess.uci.Score(None, score.mate * polarity)
    else:
        return chess.uci.Score(score.cp * polarity, None)

def should_investigate(a, b, board):
    """ determine if the difference between scores A and B
        makes the position worth investigating for a puzzle.

        A and B are normalized scores (scores from white's perspective)
    """
    if a.cp is not None and material_total(board) > 3:
        if b.cp is not None and material_count(board) > 6:
            # from an even position, the position changed by more than 1.1 cp
            if abs(a.cp) < 110 and abs(b.cp - a.cp) >= 110:
                return True
            # from a winning position, the position is now even
            if abs(a.cp) > 200 and abs(b.cp) < 110:
                return True
            # from a winning position, a player blundered into a losing position
            if abs(a.cp) > 200 and sign(b) != sign(a):
                return True
        elif b.mate:
            # from an even position, someone is getting checkmated
            if abs(a.cp) < 110:
                return True
    elif a.mate and b.mate:
        # a player blundered from a checkmating position into being checkmated
        if sign(a) != sign(b):
            return True
    return False
