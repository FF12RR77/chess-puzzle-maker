#!/usr/bin/env python

"""Creating chess puzzles for lichess.org"""

import argparse
import chess
import chess.uci
import chess.pgn
import logging
import os
import sys

from modules.bcolors import bcolors
from modules.fishnet import stockfish_command
from modules.puzzle.puzzle import Puzzle
from modules.investigate import should_investigate

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument("threads", metavar="THREADS", nargs="?", type=int, default=4,
                    help="number of engine threads")
parser.add_argument("memory", metavar="MEMORY", nargs="?", type=int, default=2048,
                    help="memory in MB to use for engine hashtables")
parser.add_argument("--depth", metavar="DEPTH", nargs="?", type=int, default=15,
                    help="depth for stockfish analysis")
parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
parser.add_argument("--games", metavar="GAMES", default="games.pgn",
                    help="A specific pgn with games")
parser.add_argument("--strict", metavar="STRICT", default=True,
                    help="If False then it will be generate more tactics but maybe a little ambiguous")
settings = parser.parse_args()
try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stdout)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
logging.getLogger("chess.uci").setLevel(logging.WARNING)

engine = chess.uci.popen_engine(stockfish_command())
engine.setoption({'Threads': settings.threads, 'Hash': settings.memory})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

all_games = open(settings.games, "r")
tactics_file = open("tactics.pgn", "w")
game_id = 0

while True:
    game = chess.pgn.read_game(all_games)
    if game == None:
        break
    node = game

    game_id = game_id + 1 
    logging.debug(bcolors.HEADER + "Game ID: " + str(game_id) + bcolors.ENDC)
    logging.debug(bcolors.WARNING + str(game)  + bcolors.ENDC)
    
    prev_score = chess.uci.Score(None, None)
    puzzles = []
    
    logging.debug(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
    logging.debug("Analysing Game..." + bcolors.ENDC)
    
    engine.ucinewgame()
    
    while not node.is_end():
        next_node = node.variation(0)
        engine.position(next_node.board())
        engine.go(depth=settings.depth)
        cur_score = info_handler.info["score"][1]
        logging.debug(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        if cur_score.mate:
            logging.debug(bcolors.OKBLUE + "   Mate: " + str(cur_score.mate) + bcolors.ENDC)
        else:
            logging.debug(bcolors.OKBLUE + "   CP: " + str(cur_score.cp) + bcolors.ENDC)
        if should_investigate(prev_score, cur_score, node.board()):
            # Found a possible puzzle
            logging.debug(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(Puzzle(node.board(), next_node.move, str(game_id), engine, info_handler, game, settings.strict))
    
        prev_score = cur_score
        node = next_node

    logging.debug(bcolors.WARNING + "# positions to consider as puzzles = " + str(len(puzzles)))
    for i, puzzle in enumerate(puzzles):
        logging.debug("")
        logging.debug(bcolors.HEADER + ("Considering position %d of %d..." % (i+1, len(puzzles))) + bcolors.ENDC)
        # use depth 24 to explore puzzle positions
        puzzle.generate(24)
        if puzzle.is_complete():
            puzzle_pgn = str(puzzle.to_pgn())
            logging.debug(bcolors.WARNING + "NEW PUZZLE GENERATED" + bcolors.ENDC)
            logging.info(bcolors.OKBLUE + puzzle_pgn + bcolors.ENDC)
            tactics_file.write(puzzle_pgn)
            tactics_file.write("\n\n")

tactics_file.close()
