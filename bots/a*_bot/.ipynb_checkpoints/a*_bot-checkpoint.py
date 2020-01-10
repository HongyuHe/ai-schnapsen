from api import Deck, State, util
from queue import PriorityQueue


class Bot:
    __WIN_SCORE = 66
    __NUM_BELIEF_STATES = 1

    __A_star_fringe = PriorityQueue()

    def __init__(self):
        pass

    def get_move(self, state) -> (int, int):

        me = state.whose_turn()
        depth = 0                               # root
        available_moves = state.moves()
        scores = [0.0] * len(available_moves)

        for i, move in enumerate(available_moves):
            # print(f"----------- Me({me}) starts trying {i}th Move {move} ------------- ")
            for _ in range(self.__NUM_BELIEF_STATES + 1):
                next_state = self.assume_next_state(move, state)
                # print(f"----------- Assumed next moves {next_state.moves()} ------------- ")
                scores[i] += self.A_star_eval(me, depth+1, next_state.clone())

                self.__A_star_fringe = PriorityQueue()
            scores[i] /= self.__NUM_BELIEF_STATES

        print(scores)
        return available_moves[scores.index(max(scores))]


    def A_star_eval(self, me, depth, curr_state) -> float:  # using BFS for now
        # print(f"Turn: {curr_state.whose_turn()}, Me {me}")
        if curr_state.finished():
            winner = curr_state.winner()[0]
            win_points = curr_state.winner()[1]
            pole = 1
            if winner != me:
                pole = -1
                # print("lose")
                # print("Winner:", curr_state.winner()[0], " Looser Me: ", me)
                # print (curr_state.get_points(1), curr_state.get_points(util.other(1)))
                # print("Diff: ", util.difference_points(curr_state, winner))
                # print ("Winner: ", curr_state.winner()[1])
                # return self.win_score_heuristic(me, depth, curr_state)
                # return float("-inf")
            # else:
                # print("win")
                # return self.win_score_heuristic(me, depth, curr_state)
                # print("Winner:", curr_state.winner()[0], " Winner Me: ", me)
                # print (curr_state.get_points(me) - curr_state.get_points(util.other(me)))
                # print("Diff: ", util.difference_points(curr_state, winner))
                # return (curr_state.get_points(me) - curr_state.get_points(util.other(me)))
            # print(pole*(util.difference_points(curr_state, winner) + win_points))
            return pole*(util.difference_points(curr_state, winner) + win_points)

        next_moves = curr_state.moves()
        if str(type(next_moves)) == "<class 'tuple'>":
            self.__A_star_fringe.put(
                (self.f(me, depth+1, curr_state.clone().next(next_moves)),
                 [float('-inf') if v is None else v for v in next_moves]))
        else:
            for move in next_moves:
                cost = self.f(me, depth+1, curr_state.clone().next(move))
                self.__A_star_fringe.put( (cost, [float('-inf') if v is None else v for v in move]) )
                # self.__A_star_fringe.put( (cost, move if move[0] and move[1] is not None else (move[0], float("-inf"))) )
                # print(move, " Cost: ", cost)
                # if cost < prio:
                #     choice = move
                #     prio = cost
                    # print(cost)
                # pq.put((self.f(depth, curr_state.clone().next(move)), move))
            # print(f"{curr_state.whose_turn()} Choose: ", choice)
        # if not self.__A_star_fringe.empty():
        _, choice = self.__A_star_fringe.get()
            # print(cost)
        # else:
        #     print("EMPTY!!!")
        return self.A_star_eval(me, depth+1, curr_state.next(choice))

    def f(self, me, depth, state):
        def g():
            # print("g: ", state.get_points(util.other(me)) + depth)
            return state.get_points(util.other(me)) + depth # the opponent's score

        def h():
            # print("h: ", self.__WIN_SCORE - state.get_points(me))
            return self.__WIN_SCORE - state.get_points(me)
        return g()+h()

    def assume_next_state(self, move, state):
        root = state
        curr_state = root.make_assumption() if root.get_phase() == 1 else root # only one time for now
        # if root.get_phase() == 1:
        #     curr_state.__signature = None

        return curr_state.next(move)

    def win_score_heuristic(self, player, depth, state) -> float:
        return (util.difference_points(state, player))**2 * pow(depth, -1)

