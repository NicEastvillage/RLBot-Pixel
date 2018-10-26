import math

from rlbot.agents.base_agent import SimpleControllerState

import usystem
from vec import Vec3
import vec


def ball_land_eta(packet):
    height = packet.ball_pos.z - 90
    gravity = -650
    vel = packet.ball_vel.z
    D = -2 * gravity * height + vel**2
    if D < 0:
        return 0.01
    eta1 = (-vel + math.sqrt(D)) / gravity
    eta2 = (-vel - math.sqrt(D)) / gravity
    return max(eta1, eta2)


def dribble(packet):
    eta = ball_land_eta(packet)
    ball_land_pos = Vec3().set(packet.ball_prediction.slices[int(eta * 60)].physics.location)
    enemy_goal = Vec3(y=packet.my_sign * -5120)
    car_to_enemy_goal = enemy_goal - packet.my_pos
    ball_land_pos = ball_land_pos - car_to_enemy_goal.rescale(35)
    # packet.renderer.draw_line_3d(packet.my_pos.tuple(), ball_land_pos.tuple(), packet.renderer.create_color(255, 0, 0, 255))
    return go_to_point(packet, ball_land_pos, eta)


def go_to_point(packet, point, eta):
    controls = SimpleControllerState()

    if packet.my_pos.z > 700:
        point = packet.my_pos.flat()
        eta = 0.05

    car_to_point = point - packet.my_pos
    rel_pos = vec.relative_location(packet.my_pos, point, packet.my_ori)

    ang = rel_pos.ang()

    smooth = ang + 2 * ang ** 3
    if smooth < -1:
        smooth = -1
    elif smooth > 1:
        smooth = 1
    controls.steer = smooth

    dist = rel_pos.length()
    target_vel = dist / eta
    cur_vel = packet.my_vel.proj_onto_size(car_to_point)

    if cur_vel < 0:
        controls.throttle = 0.2
    elif target_vel > 1400:
        controls.throttle = 1

        if cur_vel > target_vel:
            # break
            controls.throttle = 0.7
            controls.boost = 0
        else:
            controls.boost = 1

    else:
        if target_vel > cur_vel + 100:
            controls.throttle = 1
        elif target_vel < cur_vel - 100:
            controls.throttle = -1
        else:
            controls.throttle = 0

    return controls
