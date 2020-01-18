#!usr/bin/env python
"""
A command line program for multiple games between several bots.

For all the options run
python play.py -h
"""

from argparse import ArgumentParser
from api import State, util, engine
import random, time, os.path, importlib, sys, traceback


def tournament_load_player(name, classname='Bot', classdepth=1, classheuristic="default"):
    # Accepts a string representing a bot and returns an instance of that bot. If the name is 'random'
    # this function will load the file ./bots/random/random.py and instantiate the class "Bot"
    # from that file.

    # :param name: The name of a bot
    # :return: An instantiated Bot

    name = name.lower()
    path = './bots/{}/{}.py'.format(name, name)

    # Load the python file (making it a _module_)
    try:
        module = importlib.import_module('bots.{}.{}'.format(name, name))
    except:
        print('ERROR: Could not load the python file {}, for player with name {}. Are you sure your Bot has the right '
              'filename in the right place? Does your python file have any syntax errors?'.format(path, name))
        traceback.print_exc()
        sys.exit(1)

    # Get a reference to the class
    try:
        cls = getattr(module, classname)
        player = cls(depth=classdepth, heuristic=classheuristic) # Instantiate the class
        player.__init__(depth=classdepth, heuristic=classheuristic)
    except:
        print('ERROR: Could not load the class "Bot" {} from file {}.'.format(classname, path))
        traceback.print_exc()
        sys.exit()

    return player


def run_tournament(options):

    start_time = time.time()

    if options.players is None:
        print('Must enter name of bot to test e.g. -p "features"')
        return

    if options.heuristic is None:
        print('Must enter heuristic for bot under test to use e.g. -he "default"')
        return

    if options.depth is None:
        print("Must enter maximum depth e.g. -d 4")
        return

    log_file_name = "tournament_log.csv"

    if not os.path.exists(log_file_name):
        with open(log_file_name, 'w') as file:
            file.write('bot,depth,wins,loses\n')

    base_bot = util.load_player(options.base_bot)
    test_bot = tournament_load_player(options.players, classdepth=options.depth, classheuristic=options.heuristic)

    wins = 0
    total_games = 0

    while (time.time() - start_time <= options.game_time):

        # Generate a state with a random seed
        state = State.generate(phase=int(options.phase))

        # The bot under test is player 2
        winner, _ = engine.play(base_bot, test_bot, state, options.max_time*1000, verbose=False, fast=options.fast)

        if winner is not None:
            if winner is 2:
                wins += 1
            total_games += 1

        # The bot under test is player 1
        winner, _ = engine.play(test_bot, base_bot, state, options.max_time*1000, verbose=False, fast=options.fast)
        
        if winner is not None:
            if winner is 1:
                wins += 1
            total_games += 1
        
    with open(log_file_name, 'a') as file:
        # bot,depth,wins,loses
        file.write('{},{},{},{}\n'.format(options.players, options.depth, wins, total_games - wins))


if __name__ == "__main__":

    ## Parse the command line options
    parser = ArgumentParser()

    parser.add_argument("-b", "--base-bot",
                        dest="base_bot",
                        help="The bot which will play against the bot to test",
                        default="bully")

    parser.add_argument("-d", "--search-depth",
                        dest="depth",
                        help="Maximum search depth allowed by the bot under test",
                        type=int)

    parser.add_argument("-he", "--heuristic",
                        dest="heuristic",
                        help="The heuristic the bot under test should use")

    parser.add_argument("-gt", "--game-time",
                        dest="game_time",
                        help="Maximum run time allowed for the program in seconds (not exact, may finish early)",
                        type=int, default=840)

    parser.add_argument("-s", "--starting-phase",
                        dest="phase",
                        help="Which phase the game should start at.",
                        default=1)

    parser.add_argument("-p", "--players",
                        dest="players",
                        help="Comma-separated list of player names (enclose with quotes).")

    parser.add_argument("-r", "--repeats",
                        dest="repeats",
                        help="How many matches to play for each pair of bots",
                        type=int, default=10)

    parser.add_argument("-t", "--max-time",
                        dest="max_time",
                        help="maximum amount of time allowed per turn in seconds (default: 5)",
                        type=int, default=5)

    parser.add_argument("-f", "--fast",
                        dest="fast",
                        action="store_true",
                        help="This option forgoes the engine's check of whether a bot is able to make a decision in the allotted time, so only use this option if you are sure that your bot is stable.",
                        default=True)

    options = parser.parse_args()

    run_tournament(options)
