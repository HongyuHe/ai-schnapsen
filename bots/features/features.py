#!/usr/bin/env python

from api import State, util
import random, sys

class Bot:

    __max_depth = -1
    __randomize = True
    __heuristic = None


    def __init__(self, depth=6, heuristic="default"):
        # :param randomize: Whether to select randomly from moves of equal value (or to select the first always)
        # :param depth:

        self.__max_depth = depth

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and attr_name.find('heuristic') != -1 and attr_name.find(heuristic) != -1:
                self.__heuristic = attr

        if self.__heuristic is None:
            print('\nCould not find heuristic method containing "{}"\n'.format(heuristic))
            sys.exit(1)
        

    def get_move(self, state):
        # type: (State) -> tuple[int, int]

        _, move = self.value(state)

        return move

    def value(self, state, depth = 0):
        # type: (State, int) -> tuple[float, tuple[int, int]]

        # Return the value of this state and the associated move
        # :param state:
        # :param depth:
        # :return: A tuple containing the value of this state, and the best move for the player currently to move

        if state.finished():
            winner, points = state.winner()
            return (points, None) if winner == 1 else (-points, None)

        if depth == self.__max_depth:
            return self.__heuristic(state)

        moves = state.moves()

        if self.__randomize:
            random.shuffle(moves)

        best_value = float('-inf') if self.maximizing(state) else float('inf')
        best_move = None

        for move in moves:

            next_state = state.next(move)

            value, _ = self.value(next_state, depth + 1)

            if self.maximizing(state):
                if value > best_value:
                    best_value = value
                    best_move = move
            else:
                if value < best_value:
                    best_value = value
                    best_move = move

        return best_value, best_move

    def maximizing(self, state):
        # type: (State) -> bool

        # Whether we're the maximizing player (1) or the minimizing player (2).

        # :param state:
        # :return:

        return state.whose_turn() == 1


    # ============================================= ! I M P O R T A N T ! =============================================
    # When adding new heuristic methods, make sure the method name contains the word 'heuristic' and is otherwise unique
    # from the other heuristic methods - if two method names contain the same word, then they may not be differentiated correctly
    # when selecting the heuristic from the command line e.g.
    # given methods:
    #   def heuristic_something: ...
    #   def heuristic_something_else: ...
    # If the argument "something" is given on the command line, it is possible that "something_else" will be used incorrectly

    def heuristic_default(self, state):
        # type: (State) -> float

        # Estimate the value of this state: -1.0 is a certain win for player 2, 1.0 is a certain win for player 1

        # :param state:
        # :return: A heuristic evaluation for the given state (between -1.0 and 1.0)

        return util.ratio_points(state, 1) * 2.0 - 1.0, None

    def heuristic_example_with_some_name(self, state):
        return 1.0, None

    def heuristic_also_showing_how_to(self, state):
        return -1.0, None