from api import Deck, State, util
from queue import PriorityQueue


class Bot:
    __WIN_SCORE = 66
    __DEPTH_LIMIT = 10
    __NUM_BELIEF_STATES = 5

    __fringe = PriorityQueue()

    def __init__(self, _num_beleif_states = 5, _depth_limit = 10):
        self.__DEPTH_LIMIT = _depth_limit
        self.__NUM_BELIEF_STATES = _num_beleif_states


    ########################## heuristics ###########################


    def action_cost(self, me, depth, state) -> float:

        def backward_cost():
            # return (state.get_points(util.other(me)) + depth) / self.__WIN_SCORE  # the opponent's score + depth
            return ???

        def forward_cost():
            # return (self.__WIN_SCORE - state.get_points(me)) / self.__WIN_SCORE  # my score
            return ???

        # return backward_cost() + forward_cost()
        return ???

    def midway_eval(self, depth, me, curr_state) -> float:
        # return self.bottom_decision(depth, me, curr_state)
        return ???

    def bottom_decision(self, me, depth, curr_state) -> float:
        # pole = -1 if curr_state.winner()[0] != me else 1
        # return pole * (util.difference_points(curr_state, curr_state.winner()[0]) + curr_state.winner()[1]) * 1.5 * depth
        return ???

    ########################## heuristics ###########################


    def mind_simulation(self, me, depth, curr_state) -> float:  # using dijkstra for now

        if curr_state.finished():
            return self.bottom_decision(depth, me, curr_state)

        if depth > self.__DEPTH_LIMIT:
            return self.midway_eval(depth, me, curr_state);

        next_moves = curr_state.moves()

        if str(type(next_moves)) == "<class 'tuple'>":

            self.__fringe.put(
                (self.action_cost(me, depth + 1, curr_state.clone().next(next_moves)),
                 [float('-inf') if v is None else v for v in next_moves])
            )

        else:

            for move in next_moves:
                cost = self.action_cost(me, depth + 1, curr_state.clone().next(move))
                self.__fringe.put((cost, [float('-inf') if v is None else v for v in move]))

        _, choice = self.__fringe.get()

        return self.mind_simulation(me, depth + 1, curr_state.next(choice))


    def get_move(self, state) -> (int, int):

        depth = 0
        me = state.whose_turn()
        available_moves = state.moves()
        scores = [0.0] * len(available_moves)

        for i, move in enumerate(available_moves):
            for _ in range(self.__NUM_BELIEF_STATES + 1):
                next_state = self.assume_next_state(move, state)
                scores[i] += self.mind_simulation(me, depth + 1, next_state.clone())

                self.__fringe = PriorityQueue()
            scores[i] /= self.__NUM_BELIEF_STATES

        # print(scores)
        return available_moves[scores.index(max(scores))]


    def assume_next_state(self, move, state):
        root = state
        curr_state = root.make_assumption() if root.get_phase() == 1 else root

        return curr_state.next(move)



