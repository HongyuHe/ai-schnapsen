from api import Deck, State, util
from queue import PriorityQueue
import random


class Bot:
    __WIN_SCORE = 66
    __DEPTH_LIMIT = 3
    __NUM_BELIEF_STATES = 1 # LLN

    __me__ = 1

    __fringe = PriorityQueue()

    def __init__(self, _num_beleif_states = 1, _depth_limit = 3):
        self.__DEPTH_LIMIT = _depth_limit
        self.__NUM_BELIEF_STATES = _num_beleif_states
        self.__me__ = 1


    ########################## heuristics ###########################


    def action_cost(self, me, depth, state) -> float:

        def backward_cost():
            # return (state.get_points(util.other(me)) + depth) / self.__WIN_SCORE  # the opponent's score + depth
            return -random.random() if me == self.__me__ else random.random()

        def forward_cost():
            # return (self.__WIN_SCORE - state.get_points(me)) / self.__WIN_SCORE  # my score
            return -random.random() if me == self.__me__ else random.random()

        # return backward_cost() + forward_cost()
        return (backward_cost() + forward_cost()) / 2

    def midway_eval(self, depth, me, curr_state) -> float:
        # return self.bottom_decision(depth, me, curr_state)
        return -random.random() if me == self.__me__ else random.random()

    def bottom_decision(self, me, depth, curr_state) -> float:
        # pole = -1 if curr_state.winner()[0] != me else 1
        # return pole * (util.difference_points(curr_state, curr_state.winner()[0]) + curr_state.winner()[1]) * 1.5 * depth
        return -random.random() if me == self.__me__ else random.random()

    ########################## heuristics ###########################


    def mind_simulation(self, me, depth, curr_state) -> float:  # using dijkstra for now
        print("sim, ", me, ", d: ", depth)
        print(curr_state.__repr__)
        if curr_state.finished():
            #print("win/loss: ", depth)
            return self.bottom_decision(depth, me, curr_state)

        if depth > self.__DEPTH_LIMIT:
            #print("max depth: ", depth)
            return self.midway_eval(depth, me, curr_state)

        next_moves = curr_state.moves()
        #print(next_moves)

        if str(type(next_moves)) == "<class 'tuple'>":
            next_state = curr_state.clone().next(next_moves)
            next_player = next_state.whose_turn()
            cost = self.action_cost(next_player, depth + 1, next_state)
            print("calc: ", cost)
            self.__fringe.put((cost, curr_state.clone(), depth))
        else:
            for move in next_moves:
                next_state = curr_state.clone().next(move)
                next_player = next_state.whose_turn()
                cost = self.action_cost(next_player, depth + 1, next_state)
                print("calc: ", cost)
                self.__fringe.put((cost, curr_state.clone(), depth))

        # What is choice for?
        cost, next_state, depth = self.__fringe.get()
        print("expanding: ", cost)

        next_player = next_state.whose_turn()
        return self.mind_simulation(next_player, depth + 1, next_state)


    def get_move(self, state) -> (int, int):
        print("--------------------------------------------------------NEXT TRICK--------------------------------------------------------")
        depth = 0
        self.__me__ = state.whose_turn()
        available_moves = state.moves()
        scores = [0.0] * len(available_moves)

        for i, move in enumerate(available_moves):
            print("-------------------------------------NEXT REAL MOVE-------------------------------------")
            for _ in range(self.__NUM_BELIEF_STATES):
                print("--------------NEXT BELIEF STATE--------------")
                next_state = self.assume_next_state(move, state)
                scores[i] += self.mind_simulation(self.__me__, depth + 1, next_state.clone())

                self.__fringe = PriorityQueue()
            scores[i] /= self.__NUM_BELIEF_STATES
            print(scores[i])

        # print(scores)
        print("choosing: ", min(scores))
        #print(available_moves[scores.index(max(scores))])
        return available_moves[scores.index(min(scores))]


    def assume_next_state(self, move, state):
        root = state
        curr_state = root.make_assumption() if root.get_phase() == 1 else root

        return curr_state.next(move)



