#!/usr/bin/env python3
"""Summaries and figures for WP3 and WP4, from the CSV files grade_extra.py wrote.

    python3 summarise.py wp4      # table rows for section 7.3 and ../report/figures/fig_wp4_horizon.png
    python3 summarise.py wp3      # table rows for section 7.2 and ../report/figures/fig_wp3_tuning.png
"""

import csv
import pathlib
import re
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
FIGS = HERE.parent / 'report' / 'figures'
BLUE, RED, GREY = '#1f5fbf', '#c0392b', '#777777'
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9})


def rows(name):
    with open(HERE / name) as f:
        return list(csv.DictReader(f))


def num(r, k):
    v = r.get(k, '')
    return float(v) if v not in ('', None) else None


def rng(vals, fmt='%.3f'):
    vals = [v for v in vals if v is not None]
    if not vals:
        return '-'
    lo, hi = min(vals), max(vals)
    return fmt % lo if abs(hi - lo) < 1e-9 else (fmt + ' to ' + fmt) % (lo, hi)


def wp4():
    s3, s4 = rows('wp4_s3.csv'), rows('wp4_s4.csv')
    Ns = (10, 20, 30, 40)
    pick = lambda data, n, mode: [r for r in data if re.search(r'_N%d_.*_%s_' % (n, mode), r['bag'])]
    out = {}
    for n in Ns:
        f, w = pick(s3, n, 'future'), pick(s3, n, 'now')
        fit, hold = pick(s4, n, 'fit'), pick(s4, n, 'hold')
        out[n] = dict(
            f_pass=sum(r['verdict'] == 'PASS' for r in f), f_clear=rng([num(r, 'clearance') for r in f]),
            f_goal=rng([num(r, 'reached') for r in f], '%.1f'),
            w_contact=sum(num(r, 'clearance') <= 0 for r in w), w_clear=rng([num(r, 'clearance') for r in w]),
            fit_first=rng([num(r, 'first_within_0p2') for r in fit], '%.1f'),
            fit_mean=np.mean([num(r, 'mean_last5') for r in fit]),
            hold_never=sum(r['first_within_0p2'] in ('', None) for r in hold),
            hold_mean=np.mean([num(r, 'mean_last5') for r in hold]),
            solve_med=rng([num(r, 'solve_med') for r in f + w + fit + hold], '%.0f'),
            s3_med=[num(r, 'solve_med') for r in f + w], s4_med=[num(r, 'solve_med') for r in fit + hold],
            s3_p95=rng([num(r, 'solve_p95') for r in f + w], '%.0f'),
            s4_p95=rng([num(r, 'solve_p95') for r in fit + hold], '%.0f'),
            f_late=rng([num(r, 'late_ticks') for r in f], '%.0f'), w_late=rng([num(r, 'late_ticks') for r in w], '%.0f'),
            s4_late=rng([num(r, 'late_ticks') for r in fit + hold], '%.0f'),
            w_max=max(num(r, 'solve_max') for r in w), f_max=max(num(r, 'solve_max') for r in f),
            f_slack=rng([num(r, 'max_slack') for r in f], '%.4f'),
            fit_means=[num(r, 'mean_last5') for r in fit], hold_means=[num(r, 'mean_last5') for r in hold],
            f_clears=[num(r, 'clearance') for r in f], w_clears=[num(r, 'clearance') for r in w],
            f_lates=[num(r, 'late_ticks') for r in f], w_lates=[num(r, 'late_ticks') for r in w])
    for n in Ns:
        o = out[n]
        print('N=%d | S3 future pass %d/3, clear %s, goal %s, late %s, max %.0f ms, slack %s | S3 now contact %d/3, '
              'clear %s, late %s, max %.0f ms | S4 fit first %s, mean %.3f | hold never %d/3, mean %.3f | '
              'S3 solve med %s p95 %s | S4 med %s p95 %s late %s'
              % (n, o['f_pass'], o['f_clear'], o['f_goal'], o['f_late'], o['f_max'], o['f_slack'], o['w_contact'],
                 o['w_clear'], o['w_late'], o['w_max'], o['fit_first'], o['fit_mean'], o['hold_never'],
                 o['hold_mean'], rng(o['s3_med'], '%.0f'), o['s3_p95'], rng(o['s4_med'], '%.0f'), o['s4_p95'],
                 o['s4_late']))

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
    ax = axes[0]
    for n in Ns:
        ax.plot([n] * 3, out[n]['f_clears'], 'o', color=BLUE, ms=3, label='S3 future' if n == 10 else None)
        ax.plot([n] * 3, out[n]['w_clears'], 's', color=RED, ms=3, label='S3 now' if n == 10 else None)
    ax.axhline(0, color='k', lw=0.6)
    ax.set_xlabel('horizon N')
    ax.set_ylabel('real clearance [m]')
    ax.set_title('S3 clearance')
    ax.legend(fontsize=6)
    ax = axes[1]
    for n in Ns:
        ax.plot([n] * 3, out[n]['fit_means'], 'o', color=BLUE, ms=3, label='S4 fit' if n == 10 else None)
        ax.plot([n] * 3, out[n]['hold_means'], 's', color=RED, ms=3, label='S4 hold' if n == 10 else None)
    ax.set_xlabel('horizon N')
    ax.set_ylabel('mean distance, last 5 s [m]')
    ax.set_title('S4 distance to the ball')
    ax.legend(fontsize=6)
    ax = axes[2]
    ax.plot(Ns, [np.median(out[n]['s3_med']) for n in Ns], 'o-', color=BLUE, ms=3, label='S3 median solve')
    ax.plot(Ns, [np.median(out[n]['s4_med']) for n in Ns], 's-', color=GREY, ms=3, label='S4 median solve')
    ax.axhline(100, color='k', lw=0.6, ls='--')
    ax.text(20, 103, '0.1 s tick', fontsize=6)
    ax.set_xlabel('horizon N')
    ax.set_ylabel('solve time [ms]')
    ax2 = ax.twinx()
    ax2.plot(Ns, [np.mean(out[n]['f_lates'] + out[n]['w_lates']) for n in Ns], 'x--', color=RED, ms=4,
             label='S3 late ticks per run')
    ax2.set_ylabel('late ticks per run (S3)', color=RED)
    ax.set_title('Solve time and late ticks')
    ax.legend(fontsize=6, loc='center left')
    ax2.legend(fontsize=6, loc='lower right')
    ax.set_ylim(0, 115)
    for a in axes:
        a.set_xticks(Ns)
        a.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGS / 'fig_wp4_horizon.png', dpi=220)


def wp3():
    data = rows('wp3_s3.csv') + rows('wp3c_s3.csv')
    for r in data:
        print('%-46s clear %+.4f  goal %-6s final %.3f  turn %.2f  place %.2f  solve med %.0f max %.0f  late %s  odom %.3f  %s'
              % (r['bag'], num(r, 'clearance'), r['reached'] and '%.2f' % float(r['reached']) or '-',
                 num(r, 'final_error'), num(r, 'turn_total'), num(r, 'turn_place'), num(r, 'solve_med'),
                 num(r, 'solve_max'), r.get('late_ticks', '-'), num(r, 'odom_err'), r['verdict']))

    screen = rows('wp3_s3.csv')
    params = [('q_position', ('0.5', '5.0')), ('q_terminal', ('0.5', '5.0')), ('r_input', ('0.001', '0.05')),
              ('obstacle_penalty', ('5000.0', '50000.0')), ('safety_margin', ('0.0', '0.05')),
              ('mover_margin', ('0.0', '0.05')), ('delay_steps', ('0', '2')),
              ('max_angular_velocity', ('1.2', '2.0'))]
    default = {'q_position': '1.0', 'q_terminal': '1.0', 'r_input': '0.01', 'obstacle_penalty': '10000',
               'safety_margin': '0.02', 'mover_margin': '0.03', 'delay_steps': '1', 'max_angular_velocity': '0.8'}
    d_future = [r for r in screen if r['bag'].startswith('wp2_default')]
    d_now = [r for r in screen if r['bag'] == 'wp3_default_now']
    fig, axes = plt.subplots(2, 4, figsize=(7.2, 3.6), sharey=True)
    for ax, (p, vals) in zip(axes.ravel(), params):
        xs = [vals[0], default[p], vals[1]]
        fut = [num([r for r in screen if r['bag'] == 'wp3_%s_%s_future' % (p, vals[0])][0], 'clearance'),
               np.mean([num(r, 'clearance') for r in d_future]),
               num([r for r in screen if r['bag'] == 'wp3_%s_%s_future' % (p, vals[1])][0], 'clearance')]
        now = [num([r for r in screen if r['bag'] == 'wp3_%s_%s_now' % (p, vals[0])][0], 'clearance'),
               num(d_now[0], 'clearance'),
               num([r for r in screen if r['bag'] == 'wp3_%s_%s_now' % (p, vals[1])][0], 'clearance')]
        order = sorted(range(3), key=lambda i: float(xs[i]))
        xs, fut, now = [xs[i] for i in order], [fut[i] for i in order], [now[i] for i in order]
        ax.plot(range(3), fut, 'o-', color=BLUE, ms=3, label='future')
        ax.plot(range(3), now, 's-', color=RED, ms=3, label='now')
        ax.axhline(0, color='k', lw=0.6)
        ax.set_xticks(range(3))
        ax.set_xticklabels(xs, fontsize=6)
        ax.set_title(p, fontsize=7)
        ax.grid(alpha=0.25)
    axes[0, 0].set_ylabel('real clearance [m]')
    axes[1, 0].set_ylabel('real clearance [m]')
    axes[0, 0].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(FIGS / 'fig_wp3_tuning.png', dpi=220)


if __name__ == '__main__':
    {'wp4': wp4, 'wp3': wp3}[sys.argv[1]]()
