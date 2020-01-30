from api import Deck, State, util
from queue import PriorityQueue
from sklearn import preprocessing

import random


class Bot:
    __me = None
    __WIN_SCORE = 66
    __DEPTH_LIMIT = 10
    __NUM_BELIEF_STATES = 1

    __fringes = {  # fringes for both players
        1: PriorityQueue(),
        2: PriorityQueue()
    }

    def __init__(self, _num_beleif_states=4, _depth_limit=4):
        self.__DEPTH_LIMIT = _depth_limit
        self.__NUM_BELIEF_STATES = _num_beleif_states

    ########################## heuristics ###########################

    def action_cost(self, player, depth, curr_state) -> float:
        def backward_cost():
            eval_vec = [self.heuristic_1a(player, depth, curr_state)]
            return self.heuristics_eval(eval_vec)

        def forward_cost():
            eval_vec = [self.heuristic_2a(player, depth, curr_state)]
            return self.heuristics_eval(eval_vec)

        if self.__WIN_SCORE <= curr_state.get_points(util.other(player)):
            return -1
        elif self.__WIN_SCORE <= curr_state.get_points(player):
            return 1

        return (backward_cost() + forward_cost()) / 2

    def midway_eval(self, player, depth, curr_state) -> float:  # should be always < positive bottom decision
        eval_vec = [
            self.heuristic_3a(player, depth, curr_state),
            self.heuristic_5a(player, depth, curr_state),
            self.heuristic_5b(player, depth, curr_state)
        ]
        return self.heuristics_eval(eval_vec)

    def bottom_decision(self, player, depth, curr_state) -> float:
        eval_vec = [
            self.heuristic_4a(player, depth, curr_state),
            self.heuristic_5a(player, depth, curr_state),
            self.heuristic_5b(player, depth, curr_state)
        ]
        return self.heuristics_eval(eval_vec)


    ########################## api ###########################

    def get_move(self, state) -> (int, int):
        self.__me = state.whose_turn()
        # do not do multiple look-ahead in phase 2
        self.__NUM_BELIEF_STATES = 0 if state.get_phase() == 2 else self.__NUM_BELIEF_STATES

        depth = 0
        available_moves = state.moves()
        random.shuffle(available_moves)
        scores = [0.0] * len(available_moves)

        for i, move in enumerate(available_moves):
            for _ in range(self.__NUM_BELIEF_STATES + 1):
                next_state = self.assume_next_state(move, state)
                scores[i] += self.look_ahead(depth + 1, next_state.clone())
                # self.show_fringes()
                __fringes = {1: PriorityQueue(), 2: PriorityQueue()}  # clear the fringe

            # print("Before sim: ", scores[i])
            scores[i] /= self.__NUM_BELIEF_STATES if self.__NUM_BELIEF_STATES != 0 else 1
            # print("After sim: ", scores[i])

        # print(scores)
        return available_moves[scores.index(max(scores))]

    def look_ahead(self, depth, curr_state) -> float:  # using dijkstra for now
        player = curr_state.whose_turn()

        if curr_state.finished():
            return self.bottom_decision(player, depth, curr_state)

        if depth > self.__DEPTH_LIMIT:
            return self.midway_eval(player, depth, curr_state);

        next_moves = curr_state.moves()

        if str(type(next_moves)) == "<class 'tuple'>":  # only one move available

            self.__fringes[player].put(
                (self.action_cost(player, depth + 1, curr_state.clone().next(next_moves)),
                 [float('-inf') if v is None else v for v in next_moves])
            )
        else:

            for move in next_moves:
                cost = self.action_cost(player, depth + 1, curr_state.clone().next(move))
                self.__fringes[player].put((cost, [float('-inf') if v is None else v for v in move]))

        # self.show_fringes()
        _, choice = self.__fringes[player].get()

        return self.look_ahead(depth + 1, curr_state.next(choice))

    ########################## heuristics estimations ##############################

    def heuristic_1a(self, player: int, depth: int, curr_state: State) -> float:
        if (curr_state.get_points(util.other(player))+curr_state.get_points(player)) == 0:
            return 0
        return curr_state.get_points(util.other(player)) / (curr_state.get_points(util.other(player))+curr_state.get_points(player))

    def heuristic_1b(self, player: int, depth: int, curr_state: State) -> float:
        return curr_state.get_pending_points(util.other(player)) / (curr_state.get_pending_points(util.other(player))+curr_state.get_pending_points(player))

    def heuristic_2a(self, player: int, depth: int, curr_state: State) -> float:
        MAX_POSSIBLE_POTENTIAL_POINTS = 11
        potential_points = 0
        played_card = curr_state.get_opponents_played_card()
        if played_card is not None:
            played_card = util.get_rank(played_card)
            if played_card == 'J':
                potential_points -= 2
            elif played_card == 'Q':
                potential_points -= 3
            elif played_card == 'K':
                potential_points -= 4
            elif played_card == '10':
                potential_points -= 10
            elif played_card == 'A':
                potential_points -= 11

        return potential_points / MAX_POSSIBLE_POTENTIAL_POINTS

    def heuristic_2b(self, player: int, depth: int, curr_state: State) -> float:
        return (self.__WIN_SCORE - curr_state.get_points(player)) / self.__WIN_SCORE

    def heuristic_2c(self, player: int, depth: int, curr_state: State) -> float:
        MAX_POIN_EACH_TURN = 40 + 11 # marriage + A
        return (self.__WIN_SCORE - curr_state.get_points(player)) / MAX_POIN_EACH_TURN

    def heuristic_3a(self, player: int, depth: int, curr_state: State) -> float:
        trumprange = range(15, 20)
        trumpamount = 0
        handstrength = 0
        if curr_state.get_trump_suit == "C":
            trumprange = range(0, 5)
        elif curr_state.get_trump_suit == "D":
            trumprange = range(5, 10)
        elif curr_state.get_trump_suit == 'H':
            trumprange = range(10, 15)
        for move in curr_state.moves():
            handstrength = 3 - ((move[0] % 5) - 2)
            if move[0] in trumprange:
                trumpamount += 1
        handstrength += 5 * trumpamount
        return handstrength

    def heuristic_3b(self, player: int, depth: int, curr_state: State) -> float:
        curr_state.get_points(player) / (curr_state.get_points(util.other(player))+curr_state.get_points(player))

    def heuristic_3c(self, player: int, depth: int, curr_state: State) -> float:
        trumprange = range(15, 20)
        trumpamount = 0
        if curr_state.get_trump_suit == "C":
            trumprange = range(0, 5)
        elif curr_state.get_trump_suit == "D":
            trumprange = range(5, 10)
        elif curr_state.get_trump_suit == 'H':
            trumprange = range(10, 15)
        for move in curr_state.moves():
            if move[0] in trumprange:
                trumpamount += 1
        return trumpamount / len(curr_state.moves())

    def heuristic_4a(self, player: int, depth: int, curr_state: State) -> float:
        return 1 if curr_state.winner() == player else -1

    def heuristic_5a(self, player: int, depth: int, curr_state: State) -> float:
        return depth / self.__DEPTH_LIMIT

    def heuristic_5b(self, player: int, depth: int, curr_state: State) -> float:
        return util.difference_points(curr_state, self.__me) / self.__WIN_SCORE

    ################################### Utils #######################################
    def assume_next_state(self, move, state):
        root = state
        curr_state = root.make_assumption() if root.get_phase() == 1 else root

        return curr_state.next(move)

    def heuristics_eval(self, eval_vector):
        def linear_normalization():
            if max(eval_vector) == 0:
                return eval_vector
            return [float(i)/max(eval_vector) for i in eval_vector]

        return sum(linear_normalization()) / len(eval_vector)

    def show_fringes(self):
        for player, fringe in self.__fringes.items():
            print(f"Player {player} fringe: {fringe.queue}")
            print()
