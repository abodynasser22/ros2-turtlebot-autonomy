#!/usr/bin/env python3
"""Grade resubmission bags: plot_run.py's grade() plus the metrics the new experiments need.

    source ../env.sh
    python3 grade_extra.py ../bags/wp2/wp2_ccw_1 ../bags/wp2/wp2_default_1 --scenario s3
    python3 grade_extra.py ../bags/wp4/*s4* --scenario s4 --csv wp4_s4.csv

Added to plot_run.py's numbers, all from ground truth over the commanding window
(first non-zero command to last command):
  turn_total   total absolute heading change [rad]
  turn_place   time turning in place: speed < 0.02 m/s and |omega| > 0.1 rad/s [s]
  path         path length [m]
  odom_err     odometry against truth at the end [m]
  solve        median, p95, max solve time [ms], and ticks with a solve above t_step
  /mpc_stats   (if recorded) iterations, failed solves, late ticks, largest slack
  --window S   grade only the first S seconds after the first command (S4 uses 15.5 s, the
               normal length, because some nodes outlived their 17 s, see the experiment log)
"""

import argparse
import csv
import json
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'analysis'))
import plot_run  # noqa: E402

T_STEP = 0.1
LATE = 0.01   # s: a tick counts as late when it comes this much after its 0.1 s slot


def read_stats(path):
    """The /mpc_stats JSON lines of a bag, or [] if it was not recorded."""
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from std_msgs.msg import String

    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=str(path), storage_id='mcap'),
                rosbag2_py.ConverterOptions('', ''))
    rows = []
    while reader.has_next():
        topic, data, _ = reader.read_next()
        if topic == '/mpc_stats':
            rows.append(json.loads(deserialize_message(data, String).data))
    return rows


def grade(path, scenario, footprint, window=None):
    res = plot_run.grade(str(path), scenario, footprint)
    truth = res['truth']
    _, odom, solve, _, _, extra = plot_run.read_bag(str(path))

    # A fixed window after the first command, so a run whose node outlived its 17 s (Ctrl-C
    # swallowed during a solve) is graded over the same time as the others.
    t_end = res['t_end'] if window is None else min(res['t_end'], res['t0'] + window)
    n_ticks = None if window is None else int(round(window / T_STEP)) + 1
    keep = (truth[:, 0] >= res['t0']) & (truth[:, 0] <= t_end)
    t, x, y, th = truth[keep].T
    th = np.unwrap(th)
    speed = np.hypot(np.gradient(x, t), np.gradient(y, t))
    omega = np.gradient(th, t)
    dt = np.gradient(t)

    out = dict(bag=res['name'], scenario=scenario)
    if res.get('mover_clearance'):
        out['clearance'] = min(c for c, _ in res['mover_clearance'])
    elif res['clearance']:
        out['clearance'] = min(res['clearance'])
    if res.get('goal') is not None:
        out['reached'] = res['reached']
        out['final_error'] = res['final_error']
    if res.get('target_stats'):
        arr = np.array(extra['/target/pose'])
        tt = truth[keep, 0]
        dist = np.hypot(truth[keep, 1] - np.interp(tt, arr[:, 0], arr[:, 1]),
                        truth[keep, 2] - np.interp(tt, arr[:, 0], arr[:, 2]))
        rel = tt - res['t0']
        hit = np.nonzero(dist < 0.2)[0]
        out['first_within_0p2'] = float(rel[hit[0]]) if len(hit) else None
        out['mean_last5'] = float(dist[rel >= rel[-1] - 5.0].mean())
        out['window_end'] = float(rel[-1])

    out['turn_total'] = float(np.abs(np.diff(th)).sum())
    out['turn_place'] = float(dt[(speed < 0.02) & (np.abs(omega) > 0.1)].sum())
    out['path'] = float(np.hypot(np.diff(x), np.diff(y)).sum())
    out['min_heading_deg'] = float(np.degrees(th.min()))
    out['max_heading_deg'] = float(np.degrees(th.max()))

    ox = np.interp(truth[-1, 0], odom[:, 0], odom[:, 1])
    oy = np.interp(truth[-1, 0], odom[:, 0], odom[:, 2])
    out['odom_err'] = float(math.hypot(ox - truth[-1, 1], oy - truth[-1, 2]))

    ms = np.asarray(solve[:n_ticks]) * 1000.0
    out['solve_med'] = float(np.median(ms))
    out['solve_p95'] = float(np.percentile(ms, 95))
    out['solve_max'] = float(ms.max())
    out['solve_over_tick'] = int((ms > T_STEP * 1000.0).sum())
    out['ticks'] = int(len(ms))

    stats = read_stats(path)[:n_ticks]
    if stats:
        out['iter_med'] = float(np.median([s['iter'] for s in stats]))
        out['iter_max'] = int(max(s['iter'] for s in stats))
        out['failed'] = int(sum(not s['success'] for s in stats))
        out['late_ticks'] = int(sum(1 for s in stats if s['late_sim'] is not None and s['late_sim'] > LATE))
        out['late_max_ms'] = float(max((s['late_sim'] or 0.0) for s in stats) * 1000.0)
        out['max_slack'] = float(max(s['max_slack'] for s in stats))
    out['verdict'] = 'PASS' if plot_run.passed(res) else ('FAIL' if res.get('goal') else '-')
    return out


def fmt(v):
    if v is None:
        return '-'
    if isinstance(v, float):
        return '%.4f' % v if abs(v) < 1 else '%.2f' % v
    return str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bags', nargs='+')
    ap.add_argument('--scenario', required=True)
    ap.add_argument('--footprint', default='three')
    ap.add_argument('--csv', help='also write the rows to this CSV file')
    ap.add_argument('--window', type=float, help='grade only this many seconds after the first command')
    a = ap.parse_args()

    rows = [grade(b, a.scenario, a.footprint, a.window) for b in a.bags]
    keys = list(dict.fromkeys(k for r in rows for k in r))
    print(' | '.join(keys))
    for r in rows:
        print(' | '.join(fmt(r.get(k)) for k in keys))
    if a.csv:
        with open(a.csv, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)


if __name__ == '__main__':
    main()
