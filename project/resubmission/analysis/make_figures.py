#!/usr/bin/env python3
"""Figures for the resubmission report, drawn from SCENARIOS in mpc_node.py and from the bags.

    source ../env.sh
    python3 make_figures.py          # writes ../report/figures/*.png

fig_scenarios.png   top-down view of every scenario at one scale, from the SCENARIOS table
fig_one_tick.png    one 0.1 s tick of s3_future_1 rebuilt from the bag, and the pipeline
fig_wp2_turn.png    S3: default (clockwise) against forced counter-clockwise, heading and paths
"""

import json
import math
import pathlib
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT / 'analysis'))
import plot_run  # noqa: E402

MC = plot_run.MC
OUT = HERE.parent / 'report' / 'figures'
BLUE, RED, ORANGE, GREY = '#1f5fbf', '#c0392b', '#e67e22', '#777777'
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9})


def plank(ax, x, y, th, colour, alpha=0.35, discs=True):
    xs, ys = plot_run.plank_outline(x, y, th)
    ax.add_patch(Polygon(np.c_[xs, ys], closed=True, fc=colour, ec=colour, alpha=alpha, lw=0.8))
    if discs:
        fp = MC.FOOTPRINTS['three']
        for d in fp['offsets']:
            ax.add_patch(Circle((x + d * math.cos(th), y + d * math.sin(th)), fp['radius'],
                                fill=False, ec=colour, lw=0.6, ls=':'))


def scenarios():
    names = [('s1a', 'S1a: circle'), ('s1b', 'S1b: eight'), ('s2_030', 'S2: gap 0.30 m'),
             ('s3', 'S3: crossing'), ('s4', 'S4: ball')]
    fig, axes = plt.subplots(1, 5, figsize=(7.2, 2.3), sharey=True)
    for ax, (key, title) in zip(axes, names):
        cfg = MC.SCENARIOS[key]
        x0, x1, y0, y1 = cfg['box']
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=RED, lw=0.8, ls='--'))
        for ox, oy, r in cfg['obstacles']:
            ax.add_patch(Circle((ox, oy), r, fc=GREY, ec='k', lw=0.5))
        if cfg.get('walls'):
            for s in (1, -1):
                ax.plot([x0, x1], [s * cfg['walls']] * 2, color='k', lw=1.5)
        for m in cfg.get('movers', []):
            ax.add_patch(Circle((m['x0'], m['y0']), m['r'], fc=ORANGE, ec='k', lw=0.5))
            ax.annotate('', xy=(m['x0'], m['y0'] + m['vy'] * 8), xytext=(m['x0'], m['y0']),
                        arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1))
            ax.text(m['x0'] + 0.15, m['y0'], '0.30 m/s', color=ORANGE, fontsize=6)
        if cfg.get('target'):
            t = cfg['target']
            ax.plot(t['x0'], t['y0'], 'o', color='green', ms=4)
            ax.plot([t['x0'], t['x0'] + t['vx'] * 17], [t['y0'], t['y0'] + t['vy'] * 17], color='green', lw=1)
            ax.text(t['x0'] + 0.1, t['y0'] - 0.35, 'ball', color='green', fontsize=6)
        goal = cfg['goal']
        if goal in ('circle', 'figure8'):
            curve = plot_run.reference_curve(MC, goal)
            ax.plot(curve[:, 0], curve[:, 1], color=BLUE, lw=0.8)
        elif isinstance(goal, tuple):
            ax.plot(*goal, marker='*', color=BLUE, ms=8)
        plank(ax, 0.0, 0.0, 0.0, BLUE, discs=False)
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.set_xlim(-1.0, 3.6)
        ax.set_ylim(-2.6, 2.6)
        ax.set_xlabel('x [m]')
        ax.grid(alpha=0.25)
    axes[0].set_ylabel('y [m]')
    fig.tight_layout()
    fig.savefig(OUT / 'fig_scenarios.png', dpi=220)


def one_tick():
    raw = subprocess.run([sys.executable, str(HERE / 'one_tick.py'), str(PROJECT / 'bags/s3_future_1'), '3.0'],
                         capture_output=True, text=True, check=True).stdout
    t = json.loads(raw[raw.index('{'):])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.0, 1.1]))

    m, c = t['measured'], t['delay_compensated']
    plank(ax, m['x'], m['y'], math.radians(m['theta_deg']), GREY, alpha=0.25, discs=False)
    plank(ax, c['x'], c['y'], math.radians(c['theta_deg']), BLUE)
    path = np.array(t['predicted_path'])
    ax.plot(path[:, 0], path[:, 1], '.-', color=BLUE, ms=3, lw=0.8, label='predicted axle path, 20 steps')
    keep = MC.SCENARIOS['s3']['movers'][0]['r'] + MC.MOVER_MARGIN
    for k, (gx, gy) in zip((0, 5, 10, 15, 20), t['obstacle_ghosts_k0_5_10_15_20']):
        ax.add_patch(Circle((gx, gy), keep, fc=ORANGE, ec=ORANGE, alpha=0.6 if k == 0 else 0.18))
        ax.text(gx + 0.15, gy, 'k=%d' % k, fontsize=6, color=ORANGE, va='center')
    ax.text(1.58, -0.68, 'goal (2.0, 0.0) is off the right edge', fontsize=6, ha='right')
    ax.add_patch(Circle((0, 0), 0.01, fc=ORANGE, alpha=0.4, label='predicted obstacle, r + 0.03 m'))
    ax.set_aspect('equal')
    ax.set_xlim(0.2, 1.6)
    ax.set_ylim(-0.75, 0.6)
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.grid(alpha=0.25)
    ax.legend(loc='upper left', fontsize=6)
    ax.set_title('s3_future_1 at %.1f s' % t['time_after_first_move'])

    steps = [
        '1. Odometry: (x, y, θ) = (%.3f, %.3f, %.1f°)' % (m['x'], m['y'], m['theta_deg']),
        '2. Delay compensation with last command\n    (v, ω) = (%.2f, %.3f): (%.3f, %.3f, %.1f°)'
        % (t['previous_command']['v'], t['previous_command']['omega'], c['x'], c['y'], c['theta_deg']),
        '3. Fill the parameter slots: goal (2.0, 0.0) at every k;\n    obstacle centre from y = %.3f (k=0) to %.3f (k=20)'
        % (t['obstacle_ghosts_k0_5_10_15_20'][0][1], t['obstacle_ghosts_k0_5_10_15_20'][-1][1]),
        '4. Solve the NLP with IPOPT: %.1f ms' % t['solve_ms'],
        '5. Send the first input: v = %.2f m/s, ω = %.3f rad/s' % (t['command_sent']['v'], t['command_sent']['omega']),
    ]
    bx.set_axis_off()
    bx.set_xlim(0, 1)
    bx.set_ylim(0, 1)
    for i, s in enumerate(steps):
        y = 0.9 - i * 0.19
        bx.add_patch(FancyBboxPatch((0.02, y - 0.075), 0.96, 0.15, boxstyle='round,pad=0.01',
                                    fc='#eef3fb', ec=BLUE, lw=0.6))
        bx.text(0.05, y, s, va='center', fontsize=6.6)
        if i < len(steps) - 1:
            bx.annotate('', xy=(0.5, y - 0.115), xytext=(0.5, y - 0.075), arrowprops=dict(arrowstyle='->', lw=0.6))
    bx.set_title('One tick, every 0.1 s')
    fig.tight_layout()
    fig.savefig(OUT / 'fig_one_tick.png', dpi=220)


def wp2_turn():
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(width_ratios=[1.25, 1.0]))
    bags = PROJECT / 'resubmission' / 'bags' / 'wp2'
    for name, colour, label in (('wp2_default_%d', BLUE, 'default (clockwise)'),
                                ('wp2_ccw_%d', ORANGE, 'forced counter-clockwise')):
        for i in (1, 2, 3):
            truth, _, _, _, first, extra = plot_run.read_bag(str(bags / (name % i)))
            t = truth[:, 0] - first
            keep = (t >= 0) & (t <= 12)
            ax.plot(t[keep], np.degrees(np.unwrap(truth[keep, 3])), color=colour, lw=0.9,
                    label=label if i == 1 else None)
            bx.plot(truth[keep, 1], truth[keep, 2], color=colour, lw=0.9, label=label if i == 1 else None)
            if i == 2:
                for ts in (3.0, 4.0):
                    j = int(np.argmin(abs(t - ts)))
                    plank(bx, truth[j, 1], truth[j, 2], truth[j, 3], colour, alpha=0.3, discs=False)
    mover = np.array(extra['/mover_1/pose'])
    tm = mover[:, 0] - first
    k = (tm >= 0) & (tm <= 12)
    ay = ax.twinx()
    ay.plot(tm[k], mover[k, 2], color=GREY, ls='--', lw=0.8)
    ay.set_ylabel('obstacle y [m] (dashed)', color=GREY)
    ay.set_ylim(-2.5, 1.5)
    ax.axvline(4.0, color=GREY, lw=0.5, ls=':')
    ax.set_xlabel('time after first command [s]')
    ax.set_ylabel('heading θ [deg]')
    ax.grid(alpha=0.25)
    ax.legend(loc='lower right', fontsize=6)
    ax.set_title('Heading, three runs each')
    bx.plot([1.0, 1.0], [1.2, -1.0], color=GREY, ls='--', lw=0.8)
    for ts in (3.0, 4.0):
        bx.add_patch(Circle((1.0, 1.2 - 0.3 * ts), 0.10, fc=GREY, alpha=0.5))
        bx.text(1.13, 1.2 - 0.3 * ts, '%.0f s' % ts, fontsize=6, color=GREY, va='center')
    bx.plot(2.0, 0.0, marker='*', color='k', ms=7)
    bx.set_aspect('equal')
    bx.set_xlim(-0.2, 2.2)
    bx.set_ylim(-0.6, 0.6)
    bx.set_xlabel('x [m]')
    bx.set_ylabel('y [m]')
    bx.grid(alpha=0.25)
    bx.set_title('Paths (truth), plank at 3 and 4 s')
    fig.tight_layout()
    fig.savefig(OUT / 'fig_wp2_turn.png', dpi=220)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    scenarios()
    one_tick()
    wp2_turn()
    print('figures in', OUT)
