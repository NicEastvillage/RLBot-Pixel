import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from usystem import *
from vec import Vec3, Orientation


class PythonExample(BaseAgent):

    def initialize_agent(self):
        choices = [
            DribbleChoice(),
            CollectBoostChoice()
        ]
        self.ut = UtilitySystem(choices)

    def get_output(self, gtp: GameTickPacket) -> SimpleControllerState:
        packet = Packet(gtp, self)
        task, need = self.ut.evaluate(packet)
        controls = task.execute(packet)
        return controls


class Packet:
    def __init__(self, gtp, bot):
        info = gtp.game_cars[bot.index]
        self.index = bot.index
        self.my_sign = -1 if bot.team == 0 else 1
        self.ball_prediction = bot.get_ball_prediction_struct()
        self.my_pos = Vec3().set(info.physics.location)
        self.my_vel = Vec3().set(info.physics.velocity)
        self.my_ori = Orientation(info.physics.rotation)
        self.boost = info.boost

        self.ball_pos = Vec3().set(gtp.game_ball.physics.location)
        self.ball_vel = Vec3().set(gtp.game_ball.physics.velocity)

        self.field_info = bot.get_field_info()
        self.big_bpads = []
        self.big_bpads_state = []
        for i, pad in enumerate(self.field_info.boost_pads):
            if pad.is_full_boost:
                self.big_bpads.append(Vec3().set(pad.location))
                self.big_bpads_state.append(gtp.game_boosts[i].is_active)

        self.renderer = bot.renderer
        self.kickoff = gtp.game_info.is_kickoff_pause
