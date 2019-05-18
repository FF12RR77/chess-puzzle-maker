def ambiguous(scores):
    """
    Looks at a list of candidate scores (best move first) to determine
    if there's a single best player move

    Returns True if a clear best move can't be determined based on these scores
    """
    if len(scores) <= 1:
        return False
    # If strict == False then it will generate more tactics but more ambiguous
    # move_number = 1 if self.strict == True else 2
    best_move_score = scores[0].cp
    second_best_move_score = scores[1].cp
    if (best_move_score is not None and second_best_move_score is not None):
        if best_move_score < 210:
            # Unclear if the best move leads to a decisive advantage
            return True
        if best_move_score < 1000:
            # If the best move is decisively better than the 2nd best move
            if best_move_score > 500 and second_best_move_score < 140:
                return False
            elif best_move_score - second_best_move_score > 500:
                return False
        if second_best_move_score > 90:
            return True
    if scores[0].mate:
        if scores[1].mate:
            if (scores[0].mate > -1 and scores[1].mate > -1):
                # More than one possible mate-in-1
                return True
        elif scores[1].cp is not None:
            if scores[1].cp > 500:
                # 2nd best move is a decisive material advantage
                return True
    return False
