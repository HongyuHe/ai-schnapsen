#!usr/bin/env python
"""
A command line program for multiple games between several bots.

For all the options run
python play.py -h
"""

from argparse import ArgumentParser
from api import State, util, engine
import random, time, csv

def run_tournament(options):
    SCOPE = 7
    REPEATS = 100

    botnames = options.players.split(",")

    bots = []
    exp_bot = 0
    for i, botname in enumerate(botnames):
        if botname.startswith('exp'):
            exp_bot = i
        bots.append(util.load_player(botname))

    n = len(bots)
    wins = [0] * len(bots)
    wined_counter = [0] * len(bots)
    nbr_moves = [0] * len(bots)


    matches = [(p1, p2) for p1 in range(n) for p2 in range(n) if p1 < p2]

    totalgames = (n*n - n)/2 * options.repeats*SCOPE*SCOPE
    playedgames = 0


    with open(f"./phase-2/{'-'.join(botnames)}.csv", 'w') as csvf, open(f"./phase-2/{'-'.join(botnames)}.log", 'w') as logf:
        print('Playing {} games:'.format(int(totalgames)))
        logf.write('Playing {} games:'.format(int(totalgames)))

        writer = csv.writer(csvf)
        writer.writerow(['#Belief state', '#Depth', '#EXP. bot moves', '#Opponent bot moves', '#EXP. bot wins', '#Opponent bot wins', 'EXP. bot points', 'Total points', '#Total games'])

        for belief_state in range(1, SCOPE):
            for depth in range(1, SCOPE):
                bots[exp_bot].__init__(belief_state, depth)

                for a, b in matches:
                    for _ in range(options.repeats):
                        if random.choice([True, False]):
                            p = [a, b]
                        else:
                            p = [b, a]

                        # Generate a state with a random seed
                        state = State.generate(phase=int(options.phase))

                        winner, score, [p1_moves, p2_moves] = engine.play(bots[p[0]], bots[p[1]], state, options.max_time*1000, verbose=False, fast=options.fast)

                        if winner is not None:
                            winner = p[winner - 1]
                            wins[winner] += score

                            if winner == exp_bot:
                                wined_counter[0] += 1
                            else:
                                wined_counter[1] += 1

                        nbr_moves[0] += p1_moves
                        nbr_moves[1] += p2_moves

                        playedgames += 1
                        print('Played {} out of {:.0f} games ({:.0f}%): {} \r'.format(playedgames, totalgames, playedgames/float(totalgames) * 100, wins))
                        logf.write('Played {} out of {:.0f} games ({:.0f}%): {} \r'.format(playedgames, totalgames, playedgames/float(totalgames) * 100, wins))

                writer.writerow([belief_state, depth, nbr_moves[0], nbr_moves[1], wined_counter[0], wined_counter[1],  wins[exp_bot], sum(wins), options.repeats])

                wins = [0] * len(bots)
                wined_counter = [0] * len(bots)

    print('Last Results:')
    logf.write('Last Results:')
    for i in range(len(bots)):
        print('    bot {}: {} points'.format(bots[i], wins[i]))
        logf.write('    bot {}: {} points'.format(bots[i], wins[i]))


if __name__ == "__main__":

    ## Parse the command line options
    parser = ArgumentParser()

    parser.add_argument("-s", "--starting-phase",
                        dest="phase",
                        help="Which phase the game should start at.",
                        default=1)

    parser.add_argument("-p", "--players",
                        dest="players",
                        help="Comma-separated list of player names (enclose with quotes).",
                        default="rand,bully,rdeep")

    parser.add_argument("-r", "--repeats",
                        dest="repeats",
                        help="How many matches to play for each pair of bots",
                        type=int, default=10)

    parser.add_argument("-t", "--max-time",
                        dest="max_time",
                        help="maximum amount of time allowed per turn in seconds (default: 50)",
                        type=int, default=50)

    parser.add_argument("-f", "--fast",
                        dest="fast",
                        action="store_true",
                        help="This option forgoes the engine's check of whether a bot is able to make a decision in the allotted time, so only use this option if you are sure that your bot is stable.")

    options = parser.parse_args()

    run_tournament(options)
