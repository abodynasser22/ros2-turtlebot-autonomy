#!/usr/bin/env python3
"""Write resubmission/2026-11-02-bags-index.md: every new bag, its command and its result.

    source ../env.sh
    python3 make_bags_index.py

The command is rebuilt from the bag name (the batch scripts name every bag after its settings).
The result comes from the grading CSV files; bags without a CSV row are graded here.
"""

import csv
import pathlib
import re

import grade_extra

HERE = pathlib.Path(__file__).resolve().parent
BAGS = HERE.parent / 'bags'
OUT = HERE.parent / '2026-11-02-bags-index.md'
CSVS = ['wp2_s3.csv', 'wp3_s3.csv', 'wp3c_s3.csv', 'wp4_s3.csv', 'wp4_s4.csv']
TRY = {'wp2_ccw_try1': ('ccw_bias:=1.0', 'ungated min(th,0)^2 (code version of 29 Oct 20:17, replaced)'),
       'wp2_ccw_try_w0.1': ('ccw_bias:=0.1', 'ungated (replaced code version)'),
       'wp2_ccw_try_w0.3': ('ccw_bias:=0.3', 'ungated (replaced code version)'),
       'wp2_ccw_try_b1_f05': ('ccw_bias:=1.0 ccw_free:=0.5', 'free band of 0.5 rad (replaced code version)'),
       'wp2_ccw_try_gate_b1': ('ccw_bias:=1.0', 'gated, as in the final code'),
       'wp2_ccw_try_gate_b5': ('ccw_bias:=5.0', 'gated, as in the final code'),
       'wp2_ccw_try_gate_b20': ('ccw_bias:=20.0', 'gated, as in the final code')}


def settings(name):
    """(scenario, node parameters, note) from a bag name."""
    if name in TRY:
        return 's3', '-p prediction:=future ' + ' '.join('-p ' + x for x in TRY[name][0].split()), TRY[name][1]
    m = re.match(r'wp4_N(\d+)_s([34])_(\w+?)_(\d)$', name)
    if m:
        n, sc, mode, i = m.groups()
        if sc == '3':
            return 's3', '-p prediction:=%s -p n_horizon:=%s' % (mode, n), 'run %s' % i
        return 's4', '-p goal_estimate:=%s -p noise_seed:=%s -p n_horizon:=%s' % (mode, i, n), 'seed %s' % i
    m = re.match(r'wp3c?_(\w+?)_([\d.]+)_(future|now)(?:_(\d))?$', name)
    if m:
        p, v, mode, i = m.groups()
        return 's3', '-p prediction:=%s -p %s:=%s' % (mode, p, v), ('run %s' % i) if i else 'screening'
    m = re.match(r'wp3_default_now$', name)
    if m:
        return 's3', '-p prediction:=now', 'default'
    m = re.match(r'wp2_ccw_(\d)$', name)
    if m:
        return 's3', '-p prediction:=future -p ccw_bias:=20.0', 'run %s' % m.group(1)
    m = re.match(r'wp[02]_(?:s3_)?(default|future|now)(?:_check)?(?:_(\d))?$', name)
    if m:
        mode = 'now' if 'now' in name else 'future'
        return 's3', '-p prediction:=%s' % mode, 'default'
    return '?', '?', '?'


def result(r):
    bits = []
    if r.get('clearance'):
        bits.append('clearance %+.3f m' % float(r['clearance']))
    if r.get('reached'):
        bits.append('goal %.1f s' % float(r['reached']))
    elif r.get('final_error') and r['scenario'] == 's3':
        bits.append('%.2f m short' % float(r['final_error']))
    if r.get('mean_last5'):
        first = r.get('first_within_0p2')
        bits.append('within 0.2 m at %s, mean last 5 s %.3f m' % ('%.1f s' % float(first) if first else 'never',
                                                                   float(r['mean_last5'])))
    if r.get('solve_med'):
        bits.append('solve median %.0f ms, max %.0f ms' % (float(r['solve_med']), float(r['solve_max'])))
    if r.get('late_ticks'):
        bits.append('late ticks %s' % r['late_ticks'])
    return ', '.join(bits)


def main():
    graded = {}
    for name in CSVS:
        path = HERE / name
        if path.exists():
            with open(path) as f:
                for r in csv.DictReader(f):
                    graded.setdefault(r['bag'], r)

    lines = ['# Bags of the resubmission experiments', '',
             'Every bag recorded after the presentation. All are headless Gazebo runs of 17 s, three discs,',
             'recorded with `analysis/run_headless_stats.py` (topics of `analysis/run_headless.py` plus',
             '`/mpc_stats`; `wp0` has no `/mpc_stats`). Command pattern, from `resubmission/analysis/`:', '',
             '```bash', 'source ../env.sh',
             'python3 run_headless_stats.py --outdir ../bags/<folder> <scenario> three <bag> 17 <parameters>', '```',
             '', 'S4 results use the 15.5 s window (experiment log, WP4). Results from `grade_extra.py`.', '']
    for folder in ('wp0', 'wp2', 'wp3', 'wp3c', 'wp4'):
        lines += ['## %s' % folder, '', '| bag | scenario | parameters | note | result |', '|---|---|---|---|---|']
        for bag in sorted(p for p in (BAGS / folder).iterdir() if (p / 'metadata.yaml').exists()):
            sc, params, note = settings(bag.name)
            r = graded.get(bag.name)
            if r is None:
                r = grade_extra.grade(bag, sc, 'three', 15.5 if sc == 's4' else None)
                r = {k: ('' if v is None else str(v)) for k, v in r.items()}
            lines.append('| %s | %s | `%s` | %s | %s |' % (bag.name, sc, params, note, result(r)))
        lines.append('')
    lines += ['Not used: `wp0/failed_no_tb3_env/` (two empty bags, the launch could not find turtlebot3_gazebo).', '']
    OUT.write_text('\n'.join(lines))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
