#!/usr/bin/env python3
"""Rebuild one control tick of a bag: what the node measured, predicted, solved and sent.

Every message the node publishes in one tick carries the same sim-time stamp, so the tick can
be put back together from the bag alone.

    python3 one_tick.py ../../bags/s3_future_1 3.0      # the tick nearest 3.0 s after the first move
"""

import json
import math
import sys

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

TOPICS = ('/cmd_vel', '/mpc_footprint', '/mpc_ghosts', '/mpc_prediction', '/mpc_solve_time',
          '/mover_1/pose', '/ground_truth')


def stamp(msg):
    return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9


def main(path, at):
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=path, storage_id='mcap'), rosbag2_py.ConverterOptions('', ''))
    types_ = {t.name: t.type for t in reader.get_all_topics_and_types()}
    msgs = {t: [] for t in TOPICS}
    while reader.has_next():
        topic, data, t = reader.read_next()
        if topic in msgs:
            msgs[topic].append((t * 1e-9, deserialize_message(data, get_message(types_[topic]))))

    cmds = [(stamp(m), m.twist.linear.x, m.twist.angular.z) for _, m in msgs['/cmd_vel']]
    start = next(s for s, v, w in cmds if abs(v) > 1e-3 or abs(w) > 1e-3)
    i = min(range(len(cmds)), key=lambda j: abs(cmds[j][0] - start - at))
    s_now, v, w = cmds[i]
    v_prev, w_prev = cmds[i - 1][1], cmds[i - 1][2]

    fp = next(m for _, m in msgs['/mpc_footprint'] if abs(m.markers[0].header.stamp.sec
              + m.markers[0].header.stamp.nanosec * 1e-9 - s_now) < 1e-6)
    plank = fp.markers[0].pose
    x, y = plank.position.x, plank.position.y
    yaw = 2.0 * math.atan2(plank.orientation.z, plank.orientation.w)

    gh = next(m for _, m in msgs['/mpc_ghosts'] if m.markers and abs(m.markers[0].header.stamp.sec
              + m.markers[0].header.stamp.nanosec * 1e-9 - s_now) < 1e-6)
    ghosts = [(round(c.pose.position.x, 3), round(c.pose.position.y, 3)) for c in gh.markers[:5]]

    pred = next(m for _, m in msgs['/mpc_prediction'] if abs(stamp(m) - s_now) < 1e-6)
    path = [(p.pose.position.x, p.pose.position.y) for p in pred.poses]

    # The solve-time message of this tick is the last one received before the command.
    t_cmd = next(t for t, m in msgs['/cmd_vel'] if abs(stamp(m) - s_now) < 1e-6)
    solve = [m.data for t, m in msgs['/mpc_solve_time'] if t <= t_cmd][-1]

    dt = 0.1
    px, py, pyaw = x + dt * v_prev * math.cos(yaw), y + dt * v_prev * math.sin(yaw), yaw + dt * w_prev
    mover = min(msgs['/mover_1/pose'], key=lambda tm: abs(tm[0] - t_cmd))[1].pose.position

    out = dict(time_after_first_move=round(s_now - start, 2),
               measured=dict(x=round(x, 3), y=round(y, 3), theta_deg=round(math.degrees(yaw), 1)),
               previous_command=dict(v=round(v_prev, 3), omega=round(w_prev, 3)),
               delay_compensated=dict(x=round(px, 3), y=round(py, 3), theta_deg=round(math.degrees(pyaw), 1)),
               obstacle_true_now=(round(mover.x, 3), round(mover.y, 3)),
               obstacle_ghosts_k0_5_10_15_20=ghosts,
               goal=(2.0, 0.0),
               solve_ms=round(solve * 1000, 1),
               command_sent=dict(v=round(v, 3), omega=round(w, 3)),
               predicted_path_k0=tuple(round(c, 3) for c in path[0]),
               predicted_path_k20=tuple(round(c, 3) for c in path[-1]),
               predicted_path=[tuple(round(c, 3) for c in p) for p in path])
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], float(sys.argv[2]))
