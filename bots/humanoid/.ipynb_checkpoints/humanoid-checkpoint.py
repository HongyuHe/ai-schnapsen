from api import Deck, State, util
from queue import PriorityQueue
from sklearn import preprocessing


class Bot:
    __me = None
    __WIN_SCORE = 66
    __DEPTH_LIMIT = 10
    __NUM_BELIEF_STATES = 1

    __fringes = {               # fringes for both players
        1: PriorityQueue(),
        2: PriorityQueue()
    }


    def __init__(self, _num_beleif_states=20, _depth_limit=20):
        self.__DEPTH_LIMIT = _depth_limit
        self.__NUM_BELIEF_STATES = _num_beleif_states

    ########################## heuristics ###########################

    def action_cost(self, player, depth, state) -> float:
        def backward_cost():
            return (state.get_points(util.other(player))) / self.__WIN_SCORE  # the opponent's score + depth

        def forward_cost():
            return (self.__WIN_SCORE - state.get_points(player)) / self.__WIN_SCORE  # my score --> underestimate, can be negative

        if self.__WIN_SCORE < state.get_points(util.other(player)):
            return -1
        elif self.__WIN_SCORE < state.get_points(player):
            return 1

        return (backward_cost() + forward_cost())/2

    def midway_eval(self, depth, player, curr_state) -> float:  # should be always < positive bottom decision
        return self.bottom_decision(depth, player, curr_state)

    def bottom_decision(self, player, depth, curr_state) -> float:
        return util.difference_points(curr_state, self.__me)/self.__WIN_SCORE

    ########################## heuristics ###########################

    def get_move(self, state) -> (int, int):
        self.__me = state.whose_turn()
        # do not do multiple look-ahead in phase 2
        self.__NUM_BELIEF_STATES = 0 if state.get_phase() == 2 else self.__NUM_BELIEF_STATES

        depth = 0
        available_moves = state.moves()
        scores = [0.0] * len(available_moves)

        for i, move in enumerate(available_moves):
            for _ in range(self.__NUM_BELIEF_STATES + 1):
                next_state = self.assume_next_state(move, state)
                scores[i] += self.look_ahead(depth + 1, next_state.clone())
                __fringes = {1: PriorityQueue(), 2: PriorityQueue()}  # clear the fringe

            scores[i] /= self.__NUM_BELIEF_STATES if self.__NUM_BELIEF_STATES != 0 else 1

#         print(scores)
        return available_moves[scores.index(max(scores))]

    def look_ahead(self, depth, curr_state) -> float:  # using dijkstra for now
        player = curr_state.whose_turn()

        if curr_state.finished():
            return self.bottom_decision(depth, player, curr_state)

        if depth > self.__DEPTH_LIMIT:
            return self.midway_eval(depth, player, curr_state);

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

#         self.show_fringes()
        _, choice = self.__fringes[player].get()

        return self.look_ahead(depth + 1, curr_state.next(choice))

    def assume_next_state(self, move, state):
        root = state
        curr_state = root.make_assumption() if root.get_phase() == 1 else root

        return curr_state.next(move)

    def show_fringes(self):
        for player, fringe in self.__fringes.items():
            print(f"Player {player} fringe: {fringe.queue}")
            print()
