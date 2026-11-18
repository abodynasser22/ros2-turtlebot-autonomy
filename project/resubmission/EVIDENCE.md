# Evidence for every number in the resubmission report

Each row: the number as it appears in the report, where it comes from, and how to get it again.
Bags are in `project/bags/` (graded) or `project/resubmission/bags/` (new). Commands run from
`project/analysis/` with the shell setup in `2026-10-30-experiment-log.md`.

## Environment

| number | source |
|---|---|
| do-mpc 5.1.1, CasADi 3.7.2, IPOPT 3.14.11 (MUMPS 5.4.1) | `python3 -c "import do_mpc, casadi"`, IPOPT banner |
| gz sim 8.15.0, ROS 2 Jazzy, ros_gz 1.0.24, rosbag2 0.26.11 | `gz sim --versions`, `dpkg -l` |
| AMD Ryzen 5 5600, 6 cores, 12 threads | `lscpu` |

## WP0 baseline reproduction (new runs, not in the report tables yet)

| number | source |
|---|---|
| future: PASS, 11.8 / 11.5 / 11.6 s, +0.0707 / +0.0507 / +0.0523 m | `plot_run.py ../resubmission/bags/wp0/wp0_s3_future{,_2,_3} --scenario s3 --footprint three --line` |
| now: FAIL, -0.0066 / -0.0074 / -0.0062 m, 0.90 / 1.06 / 1.07 m short | `plot_run.py ../resubmission/bags/wp0/wp0_s3_now{,_2,_3} --scenario s3 --footprint three --line` |
| one run takes 34 to 35 s of wall time | `run_headless.py` sleeps 14 + 3 + 17 s; timed with `date` |
| heading -35, -61, -90 deg at 3.4, 3.98, 4.7 s (future runs) | `/ground_truth` of `s3_future_1..3` and `wp0_s3_future*`, table in the experiment log |

## WP2 S3 turn direction

| number | source |
|---|---|
| default clockwise in 10 of 10 runs, about -90 deg | heading table in the experiment log (`wp0_s3_future*`, `wp2_default_1..3`, graded `s3_future_1..3`) |
| default: goal 11.4 to 11.5 s, clearance +0.037 to +0.052 m, turn 3.50 to 3.53 rad, in place 1.30 to 1.64 s | `grade_extra.py ../bags/wp2/wp2_default_{1,2,3} --scenario s3`, `analysis/wp2_s3.csv` |
| forced CCW (`ccw_bias:=20.0`): goal 9.74, 9.70 s (run 1 truth 0.09 m short), clearance +0.055 to +0.069 m, turn 2.01 to 2.14 rad, in place 0.03 to 0.20 s | same command, `wp2_ccw_{1,2,3}` |
| forced CCW: one solve of 169 to 193 ms, 75 to 85 iterations, about 2.0 s in; next tick 72 to 96 ms late | `/mpc_stats` of `wp2_ccw_{1,2,3}` |
| run 1 odometry 0.086 m off truth at the end | `grade_extra.py` column `odom_err` |
| Burger turn-rate limit 2.84 rad/s | `/opt/ros/jazzy/lib/python3.12/site-packages/turtlebot3_teleop/script/teleop_keyboard.py` line 51 |
| Gazebo drive limits linear acceleration only, 1.0 m/s^2 | `worlds/burger_plank.sdf` line 430 |
| S3 three discs N = 20: 432 decision variables, 383 constraints; N = 10: 222 / 193; N = 40: 852 / 763 | built solver `mpc.S.size1_in('x0')`, `size1_out('g')` |
| do-mpc: collocation, Radau, degree 2, 1 finite element; soft constraints at steps 0 to N-1; linear slack cost; no shift of the warm start | `do_mpc/controller/_controllersettings.py` lines 100 to 121, `controller/_mpc.py` lines 1119 to 1275, `optimizer.py` lines 560 to 574 and 731 to 777 |

## Report draft 2026-10-29 (sections 3, 4, 6.2, 7.1)

| number in the report | source |
|---|---|
| Radau, degree 2, one finite element, points τ = 1/3 and 1 | `do_mpc/controller/_controllersettings.py` lines 100 to 115; `casadi.collocation_points(2, 'radau')` = [0.333, 1.0] |
| stage term k = 0..N-1, terminal at N, input change at k = 0 against u_prev, linear slack cost, constraints at k = 0..N-1 only | `do_mpc/controller/_mpc.py` lines 1214 to 1275; `optimizer.py` lines 560 to 574; `nl_cons_check_colloc_points = False` |
| warm start: previous solution unchanged plus multipliers, no shift; first guess states = x0, inputs = 0 | `do_mpc/optimizer.py` lines 731 to 777; `controller/_mpc.py` lines 965 to 971 |
| IPOPT 3.14.11, MUMPS, CasADi 3.7.2; options print_level 0, sb yes, print_time 0 | IPOPT banner; `mpc_node.py` `build_TBmpc` nlpsol_opts |
| Table 1 sizes (392/343, 432/383, 412/363, 492/443, 432/383, 372/323; soft per step 5, 7, 6, 10, 7, 4) | built solver, `mpc.S.size1_in('x0')`, `size1_out('g')`, `mpc.n_eps` |
| 432 = 252 + 40 + 140; 383 = 20 x (12 + 7) + 3 | `_opt_x.f['_x']`, `['_u']`, `['_eps']` lengths; `optimizer.py` lines 940 to 990 |
| disc radii 0.269 and 0.130 m, offsets -0.167, 0, +0.167 m; sweep 0.269 m | `mpc_node.FOOTPRINTS` |
| one tick at 3.0 s of s3_future_1: (0.620, -0.028, -14.7°), last cmd (0.22, -0.787), start (0.641, -0.033, -19.2°), obstacle y 0.278 to -0.322, 54.1 ms, sent (0.22, -0.794), plan end (0.726, -0.114) | `python3 analysis/one_tick.py ../../bags/s3_future_1 3.0` |
| ball: sphere r 0.05 m, no collision, no gravity, velocity plugin | `launch/project_sim.launch.py` `target_sdf`, lines 93 to 101 |
| scenario values in Table 3 | `mpc_node.SCENARIOS`, `CIRCLE`, `FIGURE8`, `GAPS`, `POST_RADIUS` |
| seven new default S3 future runs, clearance +0.037 to +0.071 m, all PASS | `wp0_s3_future`, `_2`, `_3`, `wp2_default_check`, `wp2_default_1..3` |
| β sweep: ungated 0.1, 0.3 clockwise; ungated 1 CCW, 0.13 m short; gated 1 clockwise to about -50 deg; gated 5 and 20 CCW | `bags/wp2/wp2_ccw_try*`, experiment log WP2 table |
| Table 7 and section 7.1 numbers | `analysis/wp2_s3.csv` (`grade_extra.py`) and `/mpc_stats` |

## WP4 horizon (section 7.3, Table 9, Figure 9)

All from `analysis/wp4_s3.csv` and `analysis/wp4_s4.csv`, written by
`python3 grade_extra.py ../bags/wp4/wp4_N*_s3_* --scenario s3 --window 15.5 --csv wp4_s3.csv` (and the same for
`s4`), summarised by `python3 summarise.py wp4` (output saved in `analysis/wp4_summary.txt`).

| number | source |
|---|---|
| 222 and 852 decision variables at N = 10 and 40 (S3, three discs) | built solver, see WP2 rows |
| 10 of 24 S4 runs ran 8 s too long (about 235 solves instead of 157); node log "solver raised: ... exception set" after the CasADi KeyboardInterrupt warning | `bags/wp4/logs/*.node.log`, `/mpc_stats` sim span against bag wall span |
| window 15.5 s gives graded S4: 0.139, 0.210, 0.200 / 0.342, 0.326, 0.302 m against Table 6 0.138, 0.210, 0.200 / 0.341, 0.326, 0.301 | `grade_extra.py ../../bags/s4_* --scenario s4 --window 15.5` |
| every row of Table 9 | `wp4_summary.txt` |
| N = 10 future run 1: +0.082 m, 6.67 s turning on the spot, heading to -367 deg, not reached | `wp4_s3.csv` row `wp4_N10_s3_future_1` |
| N = 40 future run 3: odometry 0.189 m off, final error 0.198 m by truth | `wp4_s3.csv` row `wp4_N40_s3_future_3` |
| longest solve 847 ms (N = 40, now) | `wp4_s3.csv` column `solve_max` |
| largest slack 0.0004 to 0.0005 (N = 20) and up to 0.0228 (N = 40), future | `wp4_s3.csv` column `max_slack` |
| S4 p95 below 60 ms at every N (max 58.3 ms) | `wp4_s4.csv` column `solve_p95` |
| outer wheel 0.284 m/s at v = 0.22, ω = 0.8; 0.38 m/s at ω = 2.0 | b = 0.160 m from `worlds/burger_plank.sdf` (wheel_separation); 0.22 + ω x 0.08 |
| Lecture 3: kinematic vs dynamic models, reliable low-level speed controller, kinematic control for motion that is not too fast, dynamic control for fast motion, friction, slipping, impacts; bicycle, Ackermann, differential-drive kinematics | `~/r7021e_2026/docs/lectures/R7021E-Lecture-3-Modelling_of_Ground_Robots_2026.pdf`, slides 9 to 15 |
| Lecture 4: unicycle, v = (v_R + v_L)/2, ω from v_R - v_L; point moved a units along x_B gives a linear system | `R7021E-Lecture-4-Models and Model Predictive Control.pdf`, slides 7 and 12 |

## WP3 tuning (section 7.2, Tables 8 and 9, Figure 8)

| number | source |
|---|---|
| every cell of Table 8 | `analysis/wp3_s3.csv` (`grade_extra.py ../bags/wp3/* --scenario s3`), rounded to mm |
| every cell of Table 9 | `analysis/wp3c_s3.csv` (`grade_extra.py ../bags/wp3c/* --scenario s3`) |
| default future 13 of 13, +0.037 to +0.071 m, 11.4 to 11.8 s; all clockwise | graded `s3_future_1..3`, `wp0_s3_future*`, `wp2_default_check`, `wp2_default_1..3`, `wp4_N20_s3_future_1..3` |
| default now: contact in 10 of 10, -0.030 to -0.006 m | graded `s3_now_1..3`, `wp0_s3_now*`, `wp3_default_now`, `wp4_N20_s3_now_1..3` |
| ω_max 1.2: goal 0.2 to 0.4 s sooner (11.07 to 11.18 s against 11.40 to 11.51 s); turn 3.62 to 3.67 rad against 3.50 to 3.53 | `wp3_s3.csv`, `wp3c_s3.csv`, `wp2_s3.csv` |
| ω_max 1.2 now: +0.003 to +0.020 m in 4 of 4, goal 11.7 to 12.3 s in 3 of 4; future goal 0.5 to 1.2 s sooner | same; 11.70 - 11.18 = 0.52, 12.28 - 11.07 = 1.21 |
| ω_max 2.0: odometry 0.22 to 0.89 m off in 3 of 6 confirmation runs | `wp3c_s3.csv` column `odom_err` (0.257, 0.221, 0.885) |
| outer wheel 0.316 m/s at v = 0.22, ω = 1.2 | 0.22 + 1.2 x 0.08 |

## Demo recordings (2 Nov 2026, windows open, not results)

| number | source |
|---|---|
| s3_future: PASS, +0.0526 m, goal 11.5 s | `plot_run.py ../bags/final_demo_bags/s3_future --scenario s3 --footprint three --line`, takes log |
| s3_now: contact -0.0069 m, 0.92 m short; odometry 0.8865 m off at the end | same for `s3_now`; `grade_extra.py ../../bags/final_demo_bags/s3_now --scenario s3` column `odom_err` |
| s4_fit: within 0.2 m at 10.0 s (9.96), mean last 5 s 0.159 m | takes log; `grade_extra.py ... --scenario s4 --window 15.5` gives 9.96 s, 0.1591 m |
| s4_hold: never, mean last 5 s 0.322 m over 15.5 s; node killed after 8 s (226 solves) | takes log, `grade_extra.py ../../bags/final_demo_bags/s4_hold --scenario s4 --window 15.5` |
| videos 1920 x 1232, about 30 fps, 23.2 to 29.2 s | `ffprobe` on `project/videos/final_demo/*.mp4` |
