# Resubmission experiment log

Dated log of the resubmission experiments. Started Thu 29 Oct 2026 in the evening.

The work was split into work packages: WP0 environment and baseline, WP1 report sections 3 and 4,
WP2 scenario 3 turn direction, WP3 scenario 3 tuning, WP4 prediction horizon, WP5 model reflection,
WP6 response to the feedback, WP7 demo launch and recordings, WP8 packaging. Bag folders and bag
names use the same labels (`wp0`, `wp2`, ...).

## 2026-10-29: WP0, environment and baseline

### Environment

| item | value | how we read it |
|---|---|---|
| OS | Ubuntu 24.04.5 LTS | `/etc/os-release` |
| ROS 2 | Jazzy | `$ROS_DISTRO` |
| Gazebo | gz sim 8.15.0 | `gz sim --versions` |
| ros_gz | 1.0.24 | `dpkg -l ros-jazzy-ros-gz` |
| rosbag2 | 0.26.11, storage mcap | `dpkg -l ros-jazzy-rosbag2` |
| Python | 3.12.3 | `python3 --version` |
| do-mpc | 5.1.1 (installed 2026-09-21) | `do_mpc.__version__` |
| CasADi | 3.7.2 (installed 2026-09-21) | `casadi.__version__` |
| IPOPT | 3.14.11, linear solver MUMPS 5.4.1 | IPOPT banner through CasADi |
| CPU | AMD Ryzen 5 5600, 6 cores, 12 threads | `lscpu` |
| RAM | 31 GiB | `free -h` |
| host | dominique-MS-7C95 (the desktop) | `hostname` |

The graded S3 and S4 bags were recorded on this desktop on 24 Oct 2026 (bag start time of
`s3_future_1`, 03:27 CEST). The solver libraries were installed on 21 Sep 2026, so the graded runs and
the new runs use the same software and hardware.

### Shell setup for every run

A non-interactive shell does not read `~/.bashrc`, so `turtlebot3_gazebo` is not found. Every run
sources the same chain as the bashrc:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
source ~/R7021E-group6/project/ros2_ws/install/setup.bash
```

Our first two baseline runs missed the second line. The launch failed, and the bags hold no
messages. They are kept in `resubmission/bags/wp0/failed_no_tb3_env/` and are not used.

### Build and smoke test

`colcon build --symlink-install` finished in 1.8 s. The install links to `ros2_ws/src`, so the
node that runs is the source file. `python3 mpc_node.py --smoke` built and solved all five
scenarios with `success=True`, in 0.09 to 0.38 s each.

The working source is the same as `submission/ros2_ws/src` (`diff -r`). The only extra file is
`rviz/replay.rviz`. `analysis/plot_run.py` differs from `submission/analysis/plot_run.py` only in three
comment lines.

### Graded bags

All 28 graded bags are in `project/bags/`. Each folder has its `metadata.yaml` and one `.mcap`.

- S1 and S2: 16 (`s1a`, `s1b`, `s2_028` to `s2_060`, one and three discs)
- S3: `s3_future_1..3`, `s3_now_1..3`
- S4: `s4_fit_1..3`, `s4_hold_1..3`

A second copy is in `~/R7021E-project-bags-backup/`. The S3 and S4 bags are also in
`~/R7021E-bags-to-upload/`.

### Topics in the graded bags

| topic | `s3_future_1` | `s4_fit_1` |
|---|---|---|
| `/odom` | 993 | 992 |
| `/ground_truth` | 584 | 584 |
| `/cmd_vel` | 157 | 158 |
| `/mpc_prediction` | 116 | 157 |
| `/mpc_solve_time` | 116 | 157 |
| `/mover_1/pose` | 584 | absent |
| `/target/pose` | absent | 584 |
| `/mpc_footprint`, `/mpc_ghosts`, `/mpc_obstacles`, `/tf`, `/tf_static` | yes | yes |

No topic carries IPOPT iterations, status, objective or slack. WP4 adds that.

### Regrade of the graded S3 bags

`python3 plot_run.py ../bags/<bag> --scenario s3 --footprint three --line`

| bag | goal | min clearance (m) | solve median / p95 (ms) | verdict |
|---|---|---|---|---|
| s3_future_1 | 11.5 s | +0.0493 | 37.5 / 65.6 | PASS |
| s3_future_2 | 11.4 s | +0.0478 | 35.6 / 59.7 | PASS |
| s3_future_3 | 11.5 s | +0.0556 | 36.4 / 62.7 | PASS |
| s3_now_1 | stopped 1.04 m short | -0.0080 | 33.6 / 88.5 | FAIL |
| s3_now_2 | stopped 0.99 m short | -0.0068 | 32.8 / 94.3 | FAIL |
| s3_now_3 | stopped 1.59 m short | -0.0057 | 33.0 / 90.1 | FAIL |

Same as Table 2 of the graded report.

### Baseline reproduction (new runs, default parameters, headless)

Command, from `analysis/`:

```bash
python3 run_headless.py --outdir ../resubmission/bags/wp0 s3 three wp0_s3_future 17 -p prediction:=future
python3 run_headless.py --outdir ../resubmission/bags/wp0 s3 three wp0_s3_now 17 -p prediction:=now
```

Repeats 2 and 3 use the names `wp0_s3_<mode>_2` and `_3`. One run takes 34 to 35 s of wall time
(14 s Gazebo start, 3 s recorder start, 17 s node).

| bag | goal | min clearance (m) | solve median / p95 (ms) | verdict |
|---|---|---|---|---|
| wp0_s3_future | 11.8 s | +0.0707 | 35.1 / 64.1 | PASS |
| wp0_s3_future_2 | 11.5 s | +0.0507 | 36.2 / 71.8 | PASS |
| wp0_s3_future_3 | 11.6 s | +0.0523 | 37.8 / 71.8 | PASS |
| wp0_s3_now | stopped 0.90 m short | -0.0066 | 31.5 / 73.9 | FAIL |
| wp0_s3_now_2 | stopped 1.06 m short | -0.0074 | 32.1 / 79.0 | FAIL |
| wp0_s3_now_3 | stopped 1.07 m short | -0.0062 | 32.2 / 78.6 | FAIL |

Verdicts: same in 6 of 6. Contact clearance in now mode: within 0.002 m of the graded range in all
three. Future goal time: within 0.4 s. Future clearance: two runs within 0.005 m of the graded range,
the first run 0.015 m above it.

The first future run is the outlier. Heading from ground truth (read from
`/ground_truth`, time from the first non-zero command):

| bag | 3.40 s | 3.98 s | 4.70 s | 6.00 s |
|---|---|---|---|---|
| s3_future_1 | -35.9 deg | -62.4 deg | -90.1 deg | -42.0 deg |
| s3_future_2 | -34.7 | -61.1 | -88.1 | -41.6 |
| s3_future_3 | -34.8 | -61.3 | -88.8 | -42.7 |
| wp0_s3_future | -34.7 | -61.2 | -92.3 | -55.7 |
| wp0_s3_future_2 | -33.7 | -60.2 | -90.1 | -43.0 |
| wp0_s3_future_3 | -36.8 | -63.3 | -91.0 | -45.1 |

All six turn clockwise along the same path up to 4.7 s. The outlier turns back more slowly after
the crossing, and that is where its clearance is larger. Our reading: run-to-run spread in timing,
same manoeuvre. Across six future runs the clearance spans +0.048 to +0.071 m. This does not
contradict the graded claim (clear in 3 of 3). It widens the spread we report.

These numbers also reproduce the `LOG.md` headings (-35, -61, -90 deg at 3.4, 3.98, 4.7 s) that WP2
starts from.

### Template docx

`Project_report_group6.docx` holds 10 `m:oMath` elements, 3 of them in `m:oMathPara` blocks.

## 2026-10-29 (evening): WP2, S3 turn direction

WP2 uses the same S3 scenario as the graded runs. All runs: future mode,
three discs, default parameters except `ccw_bias`, recorded with `/mpc_stats`
(`resubmission/analysis/run_headless_stats.py`).

### How we forced the other direction (exploration, one run each)

| bag | change | heading at 3.4 / 3.98 / 4.7 s | result |
|---|---|---|---|
| wp2_ccw_try1 | `min(th,0)^2`, weight 1, always on | +40 / +45 / +13 deg | turned CCW, stopped 0.13 m short: the term also taxes the small negative heading needed to return to y = 0 |
| wp2_ccw_try_w0.1 | same, weight 0.1 | -32 / -58 / -86 deg | still clockwise |
| wp2_ccw_try_w0.3 | same, weight 0.3 | -20 / -44 / -69 deg | still clockwise, less turn |
| wp2_ccw_try_b1_f05 | cost only below -0.5 rad, weight 1 | -27 / -32 / -56 deg | still clockwise, waits at x = 0.62 m |
| wp2_ccw_try_gate_b1 | cost gated on obstacle above robot, weight 1 | -17 / -42 / -50 deg | still clockwise, goal 11.0 s |
| wp2_ccw_try_gate_b5 | gated, weight 5 | +52 / +40 / +7 deg | CCW; node stopped on odometry, truth 0.09 m short |
| wp2_ccw_try_gate_b20 | gated, weight 20 | +52 / +37 / +2 deg | CCW, goal 9.7 s, +0.069 m |

The chosen form: `ccw_bias * gate * min(th, 0)^2` with `gate = 0.5 (1 + tanh((oy1 - y)/0.05))` and
`ccw_bias = 20`. The gate is 1 while the obstacle centre is above the robot and 0 once it is
below. The solver needed a large push to leave the clockwise side; small pushes only made the
clockwise turn smaller.

### Default against forced counter-clockwise, three runs each

`python3 grade_extra.py ../bags/wp2/wp2_default_{1,2,3} ../bags/wp2/wp2_ccw_{1,2,3} --scenario s3 --csv wp2_s3.csv`

| bag | clearance (m) | goal (s) | total turn (rad) | turn in place (s) | path (m) | heading range (deg) | odom err end (m) | solve med / p95 / max (ms) | iter max | late ticks | max slack |
|---|---|---|---|---|---|---|---|---|---|---|---|
| wp2_default_1 | +0.0491 | 11.46 | 3.50 | 1.64 | 2.09 | -89 to +15 | 0.017 | 36.0 / 59.9 / 89.3 | 40 | 0 | 0.0005 |
| wp2_default_2 | +0.0523 | 11.51 | 3.53 | 1.50 | 2.09 | -92 to +14 | 0.033 | 35.5 / 60.5 / 87.7 | 41 | 0 | 0.0004 |
| wp2_default_3 | +0.0368 | 11.40 | 3.51 | 1.30 | 2.10 | -88 to +15 | 0.013 | 34.4 / 56.7 / 83.4 | 39 | 0 | 0.0005 |
| wp2_ccw_1 | +0.0549 | 0.09 m short (truth) | 2.01 | 0.20 | 2.05 | -13 to +51 | 0.086 | 33.4 / 50.6 / 187.0 | 85 | 1 | 0.0010 |
| wp2_ccw_2 | +0.0688 | 9.74 | 2.14 | 0.03 | 2.05 | -9 to +56 | 0.033 | 33.3 / 48.5 / 169.0 | 75 | 1 | 0.0009 |
| wp2_ccw_3 | +0.0632 | 9.70 | 2.10 | 0.14 | 2.04 | -11 to +54 | 0.030 | 32.8 / 51.9 / 193.2 | 84 | 1 | 0.0009 |

`wp2_ccw_1`: the node stopped because odometry said it was within 0.05 m of the goal. Ground truth
was 0.09 m away; odometry was 0.086 m off. The controller did its job; the grader uses truth.

In every forced run one solve, about 2.0 s after the first solve, takes 169 to 193 ms with 75 to
85 IPOPT iterations. That is the tick where the plan switches to the counter-clockwise side. The
next tick comes 72 to 96 ms late (sim time).

### What it means

- Default: clockwise in 10 of 10 runs (WP0 and WP2). The plank swings to about -90 deg and the
  robot turns on the spot for 1.3 to 1.6 s.
- Forced counter-clockwise: the robot turns up to about +50 deg, drives up and behind the obstacle,
  and reaches the goal 1.7 to 1.8 s sooner with equal or larger clearance, half the turning and
  almost no turning in place.
- **This contradicts a graded claim.** The graded report says turning on the spot "is the only way
  it has to pull the front of the plank back from the obstacle's path". It is not the only way.
  The counter-clockwise manoeuvre is another, and in our runs a better one on goal time and turning.
- The examiner's point is supported: turning up is better here. Our explanation for why the solver
  picks clockwise: the cost has no heading term, the horizon reaches 0.44 m, and the solver keeps
  the local solution it is warm-started from. Small heading penalties did not move it to the other
  side. This is a local optimum of a nonconvex problem, not the best plan. We did not prove this.

## 2026-10-29 (night): WP3, S3 tuning

Batch `analysis/batch_wp3_wp4.sh` (screening, one run per value, both modes, 33 bags in `bags/wp3/`) and
`analysis/batch_wp3_confirm.sh` (three settings, three runs each, both modes, 18 bags in `bags/wp3c/`).
Graded with `grade_extra.py ... --scenario s3 --csv wp3_s3.csv` and `wp3c_s3.csv`; per-run lines in
`analysis/wp3_summary.txt`; figure `report/figures/fig_wp3_tuning.png`.

Screening (clearance future / now, m):

| parameter | lower | higher |
|---|---|---|
| q_position 1.0 | 0.5: +0.049 / -0.008 | 5.0: +0.049 / -0.005 |
| q_terminal 1.0 | 0.5: +0.053 / -0.009 | 5.0: +0.062 (stopped on odometry, 0.13 m short) / -0.007 |
| r_input 0.01 | 0.001: +0.044 / -0.006 | 0.05: +0.052 / -0.008 |
| obstacle_penalty 1e4 | 5000: +0.047 / -0.009 | 50000: +0.045 / -0.007 |
| safety_margin 0.02 | 0.0: +0.029 / -0.017 | 0.05: +0.073 / -0.002 |
| mover_margin 0.03 | 0.0: +0.021 / -0.012 | 0.05: +0.070 / -0.003 |
| delay_steps 1 | 0: +0.059 / -0.008 | 2: +0.039 / -0.005 |
| max_angular_velocity 0.8 | 1.2: +0.047 / **+0.011** | 2.0: +0.050 / **+0.016** |

Confirmation (three runs each):

- max_angular_velocity 1.2: future 3/3, +0.043 to +0.049 m, 11.1 to 11.2 s. Now: no contact 3/3,
  +0.003 to +0.020 m, goal 11.7 s in two; run 2 stopped on odometry 0.13 m short (odometry 0.129 m off).
- max_angular_velocity 2.0: future clear 3/3, +0.047 to +0.052 m; runs 2 and 3 stopped on odometry 0.26 and
  0.23 m short. Now: no contact 3/3, +0.003 to +0.021 m, goal 12.7 and 12.9 s; run 3 odometry 0.885 m off.
- safety_margin 0.05: future 3/3, +0.075 to +0.086 m (run 2 stopped on odometry 0.09 m short). Now:
  contact 3/3, -0.004 to -0.001 m.

**Surprising, weakens the graded S3 conclusion.** With a turn limit of 1.2 rad/s (Burger limit 2.84 rad/s)
the position-now controller kept clear in 4 of 4 runs (screening plus three), by 3 to 20 mm. The graded
result (contact in 3 of 3) holds at 0.8 rad/s, the Lab 2 value. Knowing the future still gives more
clearance (+0.043 to +0.049 m) and an earlier goal (0.5 to 1.2 s). Written into section 7.2 and
section 11 of the report; the graded Table 5 is unchanged.

## 2026-10-29 (night): WP4, horizon

Batch `analysis/batch_wp3_wp4.sh`, 48 bags in `bags/wp4/`. Graded with `--window 15.5`, summary in
`analysis/wp4_summary.txt`, figure `report/figures/fig_wp4_horizon.png`.

**Found while grading:** in 10 of the 24 S4 runs (none of S3) the node ran 8 s past its 17 s. The
harness's Ctrl-C arrived during an IPOPT solve; CasADi printed `KeyboardInterruptException` and returned
an error, `_tick`'s `except Exception` around `make_step` caught it, and the node kept spinning until
the harness killed it 8 s later. So these runs commanded for about 23.5 s and the ball drove out of the
box. This is behaviour of the submitted node at shutdown only; the graded bags all have about 157
solves and are not affected. We graded every WP4 run over the first 15.5 s after the first command (the
normal length). Over that window the graded S4 bags reproduce Table 6 to within 1 mm. The node code
was not changed.

Results (also Table 10 of the report):

| N | S3 future | S3 now | S4 fit mean last 5 s | S4 hold mean | S3 median solve | S3 late ticks (future; now) |
|---|---|---|---|---|---|---|
| 10 | 2/3 pass (run 1 spun 6.7 s, not reached) | contact 3/3 | 0.218 m | 0.305 m | 15 to 19 ms | 0; 0 |
| 20 | 3/3 | contact 3/3 (one at -0.030 m) | 0.184 m | 0.310 m | 32 to 37 ms | 0; 2 to 4 |
| 30 | 3/3 | contact 3/3 | 0.171 m | 0.364 m | 47 to 54 ms | 3 to 7; 4 to 9 |
| 40 | 2/3 (run 3 odometry 0.19 m off) | contact 3/3 | 0.125 m | 0.374 m | 62 to 73 ms | 10 to 11; 13 to 17 |

Against our hypotheses before the runs: the fit got better with N, not worse. The optional slowed-Gazebo rerun
was not done.

Machine use: the WP3 and WP4 batches ran while report builds, LibreOffice conversions and grading ran
on the same 12-thread machine; the first five confirmation runs ran during WP4 grading. Their solve
times are in line with the later runs (median 31 to 36 ms), but we did not measure the effect.

## 2026-10-29 (night): WP7 and WP8

- `launch/project_sim.launch.py`: new argument `rviz` (default false) opens RViz with `rviz/project.rviz`.
  Checked with `--show-args` before the recordings.
- Bags index: `2026-11-02-bags-index.md` (119 bags), from `analysis/make_bags_index.py`.

## 2026-11-02: demo recordings and upload

The four demo recordings were made by hand, following `2026-11-02-final-recording-runsheet.md`:
`s3_future`, `s3_now`, `s4_fit`, `s4_hold`, one take each, all kept. They use the graded settings and
were recorded the same way as every other bag (Gazebo, then the recorder, then the node for 17 s, the
same topics), but with the Gazebo window and RViz open (`gui:=true rviz:=true`), because the clips must
show the Gazebo world. The windows slow the solver (LOG.md, decision D1), so these bags are demo bags.
No number in the report comes from them. Graded from ground truth (`final-demo-takes.txt`):

| take | result | graded headless runs |
|---|---|---|
| s3_future | passed, +0.053 m, goal 11.5 s | +0.048 to +0.056 m, 11.4 to 11.5 s |
| s3_now | contact, -0.007 m, 0.92 m short | -0.006 to -0.008 m, 0.99 to 1.59 m short |
| s4_fit | within 0.2 m at 10.0 s, mean last 5 s 0.159 m | seed 1: 8.9 s, 0.138 m |
| s4_hold | never within 0.2 m, mean last 5 s 0.322 m | seed 1: never, 0.341 m |

In `s4_hold` the node did not stop at 17 s and was killed 8 s later (the shutdown behaviour of WP4), so
it is graded over the 15.5 s window. The clip was stopped at 17 s and is not affected.

The videos (`project/videos/final_demo/*.mp4`, 1920 x 1232, about 30 fps, 23 to 29 s) show the Gazebo
window on the left and RViz on the right.

All bags are on Google Drive, in the shared `rosbags` folder
(https://drive.google.com/drive/folders/12L4lde5OWxL0HeAs8bfUDHpDjbkt-93W):
"first submission bags" holds the graded runs, and "resubmission bags"
(https://drive.google.com/drive/folders/1yP-8rQfygHrl3je6XZWegchj1ggjevaW) holds `wp0`, `wp2`, `wp3`,
`wp3c`, `wp4` and `final_demo_bags`. Each of the 119 experiment bags was checked on the Drive for its
`.mcap` and `metadata.yaml`. The local copies of the experiment bags were then removed to free disk
space, together with the two batch log files, which only listed "bag ok" per run.
