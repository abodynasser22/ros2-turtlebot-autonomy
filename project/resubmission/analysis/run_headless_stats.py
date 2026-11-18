#!/usr/bin/env python3
"""analysis/run_headless.py, unchanged, plus /mpc_stats in the recorded topics.

Same arguments as run_headless.py. Always pass --outdir, so nothing lands in project/bags/:

    python3 run_headless_stats.py --outdir ../bags/wp2 s3 three wp2_ccw_1 17 -p ccw_bias:=1.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'analysis'))
import run_headless  # noqa: E402

if '--outdir' not in sys.argv:
    sys.exit('Give --outdir, so the bag goes into resubmission/bags/.')

run_headless.TOPICS.append('/mpc_stats')
run_headless.main()
