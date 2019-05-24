from typing import List, Optional
from collections import namedtuple
import shutil

from chess.engine import SimpleEngine, Limit, Score

from modules.fishnet import stockfish_command
from modules.utils import sign

AnalyzedMove = namedtuple("AnalyzedMove", ["move", "move_san", "score"])


class AnalysisEngine(object):
    """ Light wrapper around chess.engine
    """
    engine: SimpleEngine = None

    @staticmethod
    def instance() -> SimpleEngine:
        if not AnalysisEngine.engine:
            AnalysisEngine.engine = SimpleEngine.popen_uci(_stockfish_command())
        return AnalysisEngine.engine

    @staticmethod
    def name() -> str:
        return AnalysisEngine.instance().id["name"]

    @staticmethod
    def quit():
        if AnalysisEngine.engine:
            AnalysisEngine.engine.quit()
            AnalysisEngine.engine = None

    def best_move(board, depth) -> AnalyzedMove:
        info = AnalysisEngine.instance().analyse(board, Limit(depth=depth))
        if info.get("pv"):
            best_move = info["pv"][0]
        else:
            best_move = None
        score = info["score"].white()
        return AnalyzedMove(best_move, board.san(best_move), score)

    def best_moves(board, depth, multipv=3) -> List[AnalyzedMove]:
        best_moves = []
        infos = AnalysisEngine.instance().analyse(board, Limit(depth=depth), multipv=multipv)
        for info in infos:
            move = info["pv"][0]
            score = info["score"].white()
            best_moves.append(AnalyzedMove(move, board.san(move), score))
        return best_moves

    def evaluate_move(board, move, depth) -> AnalyzedMove:
        info = AnalysisEngine.instance().analyse(board, Limit(depth=depth), root_moves=[move])
        assert move == info["pv"][0]
        score = info["score"].white()
        return AnalyzedMove(move, board.san(move), score)

    def score(board, depth) -> Score:
        info = AnalysisEngine.instance().analyse(board, Limit(depth=depth))
        return info["score"].white()


def ambiguous_best_move(scores: List[Score]) -> bool:
  """
  Looks at a list of candidate scores (best move first) to determine
  if there's a single best player move

  Returns True if a clear best move can't be determined based on these scores
  """
  if len(scores) <= 1:
      return False
  best_move_score = scores[0].score()
  second_best_move_score = scores[1].score()
  if (best_move_score is not None and second_best_move_score is not None):
      score_change = abs(second_best_move_score - best_move_score)
      if abs(best_move_score) < 50:
          # From equality, greater than 110 cp diff
          if score_change > 110:
              return False
      if best_move_score < 210:
          # Significant difference between best move and 2nd best
          if score_change > 250:
              return False
          # Slight advantage vs equality
          if abs(second_best_move_score) < 50 and score_change > 110:
              return False
          # Slight advantage vs slight disadvantage
          if sign(scores[0]) != sign(scores[1]) and score_change > 120:
              return False
          # Unclear if the best move leads to a decisive advantage
          return True
      if best_move_score < 1000:
          # If the best move is decisively better than the 2nd best move
          if best_move_score > 350 and second_best_move_score < 140:
              return False
          elif best_move_score - second_best_move_score > 500:
              return False
      if second_best_move_score > 90:
          return True
  if scores[0].is_mate():
      if scores[1].is_mate():
          if (scores[0].mate() > -1 and scores[1].mate() > -1):
              # More than one possible mate-in-1
              return True
      elif second_best_move_score:
          if second_best_move_score > 500:
              # 2nd best move is a decisive material advantage
              return True
  return False


def _stockfish_command() -> Optional[str]:
    cmd = stockfish_command()
    if shutil.which(cmd):
        return stockfish_command()
    else:
        return shutil.which("stockfish")
