import math

import moves
from vec import Vec3
import vec


class UtilitySystem:
    def __init__(self, choices, prev_bias=0.15):
        self.choices = choices
        self.scores = [0] * len(choices)
        self.best_index = -1
        self.prev_bias = prev_bias

    def evaluate(self, data):
        for i, ch in enumerate(self.choices):
            self.scores[i] = ch.utility(data)
            if i == self.best_index:
                self.scores[i] += self.prev_bias  # was previous best choice bias

        prev_best_index = self.best_index
        self.best_index = self.scores.index(max(self.scores))

        if prev_best_index != self.best_index:
            # Check if choice has a reset method, then call it
            reset_method = getattr(self.choices[prev_best_index], "reset", None)
            if callable(reset_method):
                reset_method()

        return self.choices[self.best_index], self.scores[self.best_index]

    def reset(self):
        self.best_index = -1


def clamp01(v):
    if v < 0:
        return 0
    if v > 1:
        return 1
    return v


class DribbleChoice:
    def utility(self, packet):
        return 0.3

    def execute(self, packet):
        return moves.dribble(packet)


class CollectBoostChoice:
    def utility(self, packet):
        # boost is low
        # no threat
        if packet.kickoff:
            return 0
        boost01 = (1 - packet.boost / 100)**2
        ball_threat01 = 1 / (1 + 2 ** -0.004 * packet.ball_pos.y * packet.my_sign)
        dist_to_ball = (packet.my_pos - packet.ball_pos).length()
        dist_to_ball01 = clamp01(dist_to_ball / 4000)
        return boost01 * ball_threat01 * dist_to_ball01


    def execute(self, packet):
        best_pad_loc = Vec3()
        best_score = 999999999
        for i, pad_loc in enumerate(packet.big_bpads):
            car_to_pad = pad_loc - packet.my_pos
            dist = car_to_pad.length()
            rel_loc = vec.relative_location(packet.my_pos, pad_loc, packet.my_ori)
            ang = rel_loc.ang()
            score = dist / 5000 + abs(ang)**2
            score = score if packet.big_bpads_state else 999999999
            if packet.index == 0:
                print("boost:", i, "score:", score)
            if score < best_score:
                best_pad_loc = pad_loc

        print("Collecting boost!")
        # packet.renderer.draw_line_3d(packet.my_pos.tuple(), best_pad_loc.tuple(), packet.renderer.create_color(255, 0, 255, 0))
        return moves.go_to_point(packet, best_pad_loc, 0.01)
