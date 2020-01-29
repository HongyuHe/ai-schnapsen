from api import Deck, State, util
from queue import PriorityQueue
import random


class Bot:
    __me = None
    __WIN_SCORE = 66
    __DEPTH_LIMIT = 10
    __NUM_BELIEF_STATES = 30 # LLN

    __fringe = PriorityQueue()


    def __init__(self, _num_belief_states = 30, _depth_limit = 10):
        self.__DEPTH_LIMIT = _depth_limit
        self.__NUM_BELIEF_STATES = _num_belief_states


    def heuristic_trick_worth(self, depth, curr_state) -> float:
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


    def heuristic_negative_trick_worth(self, depth, curr_state) -> float:
        return -self.heuristic_trick_worth(depth, curr_state)


    def heuristic_pending_points(self, depth, curr_state) -> float:
        MAX_POSSIBLE_PENDING_POINTS = 100
        return -curr_state.get_pending_points(self.__me) / MAX_POSSIBLE_PENDING_POINTS


    def heuristic_opponent_pending_points(self, depth, curr_state) -> float:
        MAX_POSSIBLE_PENDING_POINTS = 100
        return -curr_state.get_pending_points(util.other(self.__me)) / MAX_POSSIBLE_PENDING_POINTS


    ########################## begin heuristics ###########################

    def action_cost(self, depth, curr_state) -> float:
        def backward_cost():
            return -random.random() if curr_state.whose_turn() == self.__me else random.random()

        def forward_cost():
            return -random.random() if curr_state.whose_turn() == self.__me else random.random()

        return (backward_cost() + forward_cost()) / 2

    def midway_eval(self, depth, curr_state) -> float:
        return self.heuristic_negative_trick_worth(depth, curr_state)

    def bottom_decision(self, depth, curr_state) -> float:
        return -1.0 if curr_state.winner()[0] == self.__me else 1.0

    ########################## end heuristics ###########################


    def mind_simulation(self, depth, curr_state) -> float:  # using dijkstra for now
        if curr_state.finished():
            return self.bottom_decision(depth, curr_state)

        if depth >= self.__DEPTH_LIMIT:
            return self.midway_eval(depth, curr_state)

        next_moves = []
        next_moves += curr_state.moves()

        for move in next_moves:
            next_state = curr_state.clone().next(move)
            cost = self.action_cost(depth + 1, next_state)
            self.__fringe.put((cost, next_state.clone(), depth))

        _, next_state, depth = self.__fringe.get()

        return self.mind_simulation(depth + 1, next_state)


    def get_move(self, state) -> (int, int):
        if self.__me == None:
            self.__me = state.whose_turn()
        
        depth = 0
        available_moves = state.moves()
        scores = [0.0] * len(available_moves)

        for i, move in enumerate(available_moves):
            for _ in range(self.__NUM_BELIEF_STATES):
                next_state = self.assume_next_state(move, state)
                scores[i] += self.mind_simulation(depth + 1, next_state)

                self.__fringe = PriorityQueue()
            scores[i] /= self.__NUM_BELIEF_STATES

        return available_moves[scores.index(min(scores))]


    def assume_next_state(self, move, state):
        curr_state = state.make_assumption() if state.get_phase() == 1 else state

        return curr_state.next(move)
