# Bags of the resubmission experiments

Every bag recorded after the presentation. All are headless Gazebo runs of 17 s, three discs,
recorded with `analysis/run_headless_stats.py` (topics of `analysis/run_headless.py` plus
`/mpc_stats`; `wp0` has no `/mpc_stats`). Command pattern, from `resubmission/analysis/`:

```bash
source ../env.sh
python3 run_headless_stats.py --outdir ../bags/<folder> <scenario> three <bag> 17 <parameters>
```

S4 results use the 15.5 s window (experiment log, WP4). Results from `grade_extra.py`.

All bags are on Google Drive, in the shared `rosbags` folder
(https://drive.google.com/drive/folders/12L4lde5OWxL0HeAs8bfUDHpDjbkt-93W). The bags below are in
"resubmission bags" (https://drive.google.com/drive/folders/1yP-8rQfygHrl3je6XZWegchj1ggjevaW), one
subfolder per folder name below; the graded runs are in "first submission bags". The local copies of
the experiment bags were removed after the upload was checked.

## wp0

| bag | scenario | parameters | note | result |
|---|---|---|---|---|
| wp0_s3_future | s3 | `-p prediction:=future` | default | clearance +0.071 m, goal 11.8 s, solve median 35 ms, max 125 ms |
| wp0_s3_future_2 | s3 | `-p prediction:=future` | default | clearance +0.051 m, goal 11.5 s, solve median 36 ms, max 116 ms |
| wp0_s3_future_3 | s3 | `-p prediction:=future` | default | clearance +0.052 m, goal 11.6 s, solve median 38 ms, max 85 ms |
| wp0_s3_now | s3 | `-p prediction:=now` | default | clearance -0.007 m, 0.90 m short, solve median 32 ms, max 150 ms |
| wp0_s3_now_2 | s3 | `-p prediction:=now` | default | clearance -0.007 m, 1.06 m short, solve median 32 ms, max 158 ms |
| wp0_s3_now_3 | s3 | `-p prediction:=now` | default | clearance -0.006 m, 1.07 m short, solve median 32 ms, max 232 ms |

## wp2

| bag | scenario | parameters | note | result |
|---|---|---|---|---|
| wp2_ccw_1 | s3 | `-p prediction:=future -p ccw_bias:=20.0` | run 1 | clearance +0.055 m, 0.09 m short, solve median 33 ms, max 187 ms, late ticks 1 |
| wp2_ccw_2 | s3 | `-p prediction:=future -p ccw_bias:=20.0` | run 2 | clearance +0.069 m, goal 9.7 s, solve median 33 ms, max 169 ms, late ticks 1 |
| wp2_ccw_3 | s3 | `-p prediction:=future -p ccw_bias:=20.0` | run 3 | clearance +0.063 m, goal 9.7 s, solve median 33 ms, max 193 ms, late ticks 1 |
| wp2_ccw_try1 | s3 | `-p prediction:=future -p ccw_bias:=1.0` | ungated min(th,0)^2 (code version of 29 Oct 20:17, replaced) | clearance +0.072 m, 0.13 m short, solve median 45 ms, max 78 ms, late ticks 0 |
| wp2_ccw_try_b1_f05 | s3 | `-p prediction:=future -p ccw_bias:=1.0 -p ccw_free:=0.5` | free band of 0.5 rad (replaced code version) | clearance +0.056 m, goal 11.3 s, solve median 35 ms, max 52 ms, late ticks 0 |
| wp2_ccw_try_gate_b1 | s3 | `-p prediction:=future -p ccw_bias:=1.0` | gated, as in the final code | clearance +0.056 m, goal 11.0 s, solve median 35 ms, max 148 ms, late ticks 1 |
| wp2_ccw_try_gate_b20 | s3 | `-p prediction:=future -p ccw_bias:=20.0` | gated, as in the final code | clearance +0.069 m, goal 9.7 s, solve median 34 ms, max 172 ms, late ticks 1 |
| wp2_ccw_try_gate_b5 | s3 | `-p prediction:=future -p ccw_bias:=5.0` | gated, as in the final code | clearance +0.063 m, 0.09 m short, solve median 34 ms, max 164 ms, late ticks 1 |
| wp2_ccw_try_w0.1 | s3 | `-p prediction:=future -p ccw_bias:=0.1` | ungated (replaced code version) | clearance +0.045 m, goal 11.5 s, solve median 36 ms, max 62 ms, late ticks 0 |
| wp2_ccw_try_w0.3 | s3 | `-p prediction:=future -p ccw_bias:=0.3` | ungated (replaced code version) | clearance +0.052 m, goal 11.3 s, solve median 35 ms, max 71 ms, late ticks 0 |
| wp2_default_1 | s3 | `-p prediction:=future` | default | clearance +0.049 m, goal 11.5 s, solve median 36 ms, max 89 ms, late ticks 0 |
| wp2_default_2 | s3 | `-p prediction:=future` | default | clearance +0.052 m, goal 11.5 s, solve median 36 ms, max 88 ms, late ticks 0 |
| wp2_default_3 | s3 | `-p prediction:=future` | default | clearance +0.037 m, goal 11.4 s, solve median 34 ms, max 83 ms, late ticks 0 |
| wp2_default_check | s3 | `-p prediction:=future` | default | clearance +0.057 m, goal 11.6 s, solve median 36 ms, max 103 ms, late ticks 0 |

## wp3

| bag | scenario | parameters | note | result |
|---|---|---|---|---|
| wp3_default_now | s3 | `-p prediction:=now` | default | clearance -0.007 m, 1.38 m short, solve median 32 ms, max 185 ms, late ticks 2 |
| wp3_delay_steps_0_future | s3 | `-p prediction:=future -p delay_steps:=0` | screening | clearance +0.059 m, goal 11.8 s, solve median 34 ms, max 114 ms, late ticks 2 |
| wp3_delay_steps_0_now | s3 | `-p prediction:=now -p delay_steps:=0` | screening | clearance -0.008 m, 1.33 m short, solve median 31 ms, max 162 ms, late ticks 2 |
| wp3_delay_steps_2_future | s3 | `-p prediction:=future -p delay_steps:=2` | screening | clearance +0.039 m, goal 11.4 s, solve median 36 ms, max 107 ms, late ticks 0 |
| wp3_delay_steps_2_now | s3 | `-p prediction:=now -p delay_steps:=2` | screening | clearance -0.005 m, 1.12 m short, solve median 31 ms, max 146 ms, late ticks 2 |
| wp3_max_angular_velocity_1.2_future | s3 | `-p prediction:=future -p max_angular_velocity:=1.2` | screening | clearance +0.047 m, goal 11.1 s, solve median 33 ms, max 85 ms, late ticks 0 |
| wp3_max_angular_velocity_1.2_now | s3 | `-p prediction:=now -p max_angular_velocity:=1.2` | screening | clearance +0.011 m, goal 12.3 s, solve median 32 ms, max 203 ms, late ticks 3 |
| wp3_max_angular_velocity_2.0_future | s3 | `-p prediction:=future -p max_angular_velocity:=2.0` | screening | clearance +0.049 m, goal 10.9 s, solve median 34 ms, max 84 ms, late ticks 0 |
| wp3_max_angular_velocity_2.0_now | s3 | `-p prediction:=now -p max_angular_velocity:=2.0` | screening | clearance +0.016 m, goal 13.0 s, solve median 32 ms, max 184 ms, late ticks 1 |
| wp3_mover_margin_0.05_future | s3 | `-p prediction:=future -p mover_margin:=0.05` | screening | clearance +0.070 m, goal 11.5 s, solve median 35 ms, max 97 ms, late ticks 0 |
| wp3_mover_margin_0.05_now | s3 | `-p prediction:=now -p mover_margin:=0.05` | screening | clearance -0.003 m, 1.24 m short, solve median 31 ms, max 260 ms, late ticks 2 |
| wp3_mover_margin_0.0_future | s3 | `-p prediction:=future -p mover_margin:=0.0` | screening | clearance +0.021 m, goal 11.4 s, solve median 35 ms, max 90 ms, late ticks 0 |
| wp3_mover_margin_0.0_now | s3 | `-p prediction:=now -p mover_margin:=0.0` | screening | clearance -0.012 m, 1.12 m short, solve median 31 ms, max 252 ms, late ticks 1 |
| wp3_obstacle_penalty_5000.0_future | s3 | `-p prediction:=future -p obstacle_penalty:=5000.0` | screening | clearance +0.047 m, goal 11.5 s, solve median 35 ms, max 82 ms, late ticks 0 |
| wp3_obstacle_penalty_5000.0_now | s3 | `-p prediction:=now -p obstacle_penalty:=5000.0` | screening | clearance -0.008 m, 1.03 m short, solve median 30 ms, max 111 ms, late ticks 2 |
| wp3_obstacle_penalty_50000.0_future | s3 | `-p prediction:=future -p obstacle_penalty:=50000.0` | screening | clearance +0.045 m, goal 11.5 s, solve median 35 ms, max 101 ms, late ticks 0 |
| wp3_obstacle_penalty_50000.0_now | s3 | `-p prediction:=now -p obstacle_penalty:=50000.0` | screening | clearance -0.006 m, 0.93 m short, solve median 32 ms, max 208 ms, late ticks 2 |
| wp3_q_position_0.5_future | s3 | `-p prediction:=future -p q_position:=0.5` | screening | clearance +0.049 m, goal 11.5 s, solve median 36 ms, max 92 ms, late ticks 0 |
| wp3_q_position_0.5_now | s3 | `-p prediction:=now -p q_position:=0.5` | screening | clearance -0.008 m, 1.08 m short, solve median 32 ms, max 174 ms, late ticks 2 |
| wp3_q_position_5.0_future | s3 | `-p prediction:=future -p q_position:=5.0` | screening | clearance +0.049 m, goal 11.5 s, solve median 35 ms, max 83 ms, late ticks 0 |
| wp3_q_position_5.0_now | s3 | `-p prediction:=now -p q_position:=5.0` | screening | clearance -0.005 m, 1.15 m short, solve median 30 ms, max 139 ms, late ticks 3 |
| wp3_q_terminal_0.5_future | s3 | `-p prediction:=future -p q_terminal:=0.5` | screening | clearance +0.053 m, goal 11.5 s, solve median 35 ms, max 98 ms, late ticks 0 |
| wp3_q_terminal_0.5_now | s3 | `-p prediction:=now -p q_terminal:=0.5` | screening | clearance -0.008 m, 1.01 m short, solve median 33 ms, max 190 ms, late ticks 2 |
| wp3_q_terminal_5.0_future | s3 | `-p prediction:=future -p q_terminal:=5.0` | screening | clearance +0.061 m, 0.13 m short, solve median 34 ms, max 112 ms, late ticks 1 |
| wp3_q_terminal_5.0_now | s3 | `-p prediction:=now -p q_terminal:=5.0` | screening | clearance -0.007 m, 1.06 m short, solve median 30 ms, max 228 ms, late ticks 2 |
| wp3_r_input_0.001_future | s3 | `-p prediction:=future -p r_input:=0.001` | screening | clearance +0.044 m, goal 11.5 s, solve median 36 ms, max 100 ms, late ticks 0 |
| wp3_r_input_0.001_now | s3 | `-p prediction:=now -p r_input:=0.001` | screening | clearance -0.006 m, 1.01 m short, solve median 31 ms, max 155 ms, late ticks 4 |
| wp3_r_input_0.05_future | s3 | `-p prediction:=future -p r_input:=0.05` | screening | clearance +0.052 m, goal 11.5 s, solve median 34 ms, max 84 ms, late ticks 0 |
| wp3_r_input_0.05_now | s3 | `-p prediction:=now -p r_input:=0.05` | screening | clearance -0.007 m, 0.98 m short, solve median 31 ms, max 160 ms, late ticks 2 |
| wp3_safety_margin_0.05_future | s3 | `-p prediction:=future -p safety_margin:=0.05` | screening | clearance +0.073 m, goal 11.5 s, solve median 35 ms, max 77 ms, late ticks 0 |
| wp3_safety_margin_0.05_now | s3 | `-p prediction:=now -p safety_margin:=0.05` | screening | clearance -0.002 m, 2.30 m short, solve median 31 ms, max 163 ms, late ticks 2 |
| wp3_safety_margin_0.0_future | s3 | `-p prediction:=future -p safety_margin:=0.0` | screening | clearance +0.029 m, goal 11.4 s, solve median 35 ms, max 94 ms, late ticks 0 |
| wp3_safety_margin_0.0_now | s3 | `-p prediction:=now -p safety_margin:=0.0` | screening | clearance -0.017 m, 1.08 m short, solve median 31 ms, max 215 ms, late ticks 1 |

## wp3c

| bag | scenario | parameters | note | result |
|---|---|---|---|---|
| wp3c_max_angular_velocity_1.2_future_1 | s3 | `-p prediction:=future -p max_angular_velocity:=1.2` | run 1 | clearance +0.043 m, goal 11.1 s, solve median 35 ms, max 93 ms, late ticks 0 |
| wp3c_max_angular_velocity_1.2_future_2 | s3 | `-p prediction:=future -p max_angular_velocity:=1.2` | run 2 | clearance +0.049 m, goal 11.1 s, solve median 35 ms, max 122 ms, late ticks 1 |
| wp3c_max_angular_velocity_1.2_future_3 | s3 | `-p prediction:=future -p max_angular_velocity:=1.2` | run 3 | clearance +0.043 m, goal 11.2 s, solve median 35 ms, max 77 ms, late ticks 0 |
| wp3c_max_angular_velocity_1.2_now_1 | s3 | `-p prediction:=now -p max_angular_velocity:=1.2` | run 1 | clearance +0.020 m, goal 11.7 s, solve median 31 ms, max 248 ms, late ticks 4 |
| wp3c_max_angular_velocity_1.2_now_2 | s3 | `-p prediction:=now -p max_angular_velocity:=1.2` | run 2 | clearance +0.003 m, 0.13 m short, solve median 31 ms, max 179 ms, late ticks 1 |
| wp3c_max_angular_velocity_1.2_now_3 | s3 | `-p prediction:=now -p max_angular_velocity:=1.2` | run 3 | clearance +0.011 m, goal 11.7 s, solve median 31 ms, max 184 ms, late ticks 1 |
| wp3c_max_angular_velocity_2.0_future_1 | s3 | `-p prediction:=future -p max_angular_velocity:=2.0` | run 1 | clearance +0.046 m, goal 11.0 s, solve median 34 ms, max 96 ms, late ticks 0 |
| wp3c_max_angular_velocity_2.0_future_2 | s3 | `-p prediction:=future -p max_angular_velocity:=2.0` | run 2 | clearance +0.048 m, 0.26 m short, solve median 34 ms, max 123 ms, late ticks 2 |
| wp3c_max_angular_velocity_2.0_future_3 | s3 | `-p prediction:=future -p max_angular_velocity:=2.0` | run 3 | clearance +0.052 m, 0.23 m short, solve median 34 ms, max 211 ms, late ticks 2 |
| wp3c_max_angular_velocity_2.0_now_1 | s3 | `-p prediction:=now -p max_angular_velocity:=2.0` | run 1 | clearance +0.014 m, goal 12.9 s, solve median 33 ms, max 173 ms, late ticks 1 |
| wp3c_max_angular_velocity_2.0_now_2 | s3 | `-p prediction:=now -p max_angular_velocity:=2.0` | run 2 | clearance +0.020 m, goal 12.7 s, solve median 33 ms, max 239 ms, late ticks 1 |
| wp3c_max_angular_velocity_2.0_now_3 | s3 | `-p prediction:=now -p max_angular_velocity:=2.0` | run 3 | clearance +0.003 m, 0.91 m short, solve median 32 ms, max 281 ms, late ticks 1 |
| wp3c_safety_margin_0.05_future_1 | s3 | `-p prediction:=future -p safety_margin:=0.05` | run 1 | clearance +0.075 m, goal 11.5 s, solve median 36 ms, max 122 ms, late ticks 1 |
| wp3c_safety_margin_0.05_future_2 | s3 | `-p prediction:=future -p safety_margin:=0.05` | run 2 | clearance +0.086 m, 0.09 m short, solve median 36 ms, max 90 ms, late ticks 0 |
| wp3c_safety_margin_0.05_future_3 | s3 | `-p prediction:=future -p safety_margin:=0.05` | run 3 | clearance +0.077 m, goal 11.5 s, solve median 35 ms, max 121 ms, late ticks 1 |
| wp3c_safety_margin_0.05_now_1 | s3 | `-p prediction:=now -p safety_margin:=0.05` | run 1 | clearance -0.001 m, 0.39 m short, solve median 31 ms, max 179 ms, late ticks 2 |
| wp3c_safety_margin_0.05_now_2 | s3 | `-p prediction:=now -p safety_margin:=0.05` | run 2 | clearance -0.003 m, 0.68 m short, solve median 32 ms, max 157 ms, late ticks 1 |
| wp3c_safety_margin_0.05_now_3 | s3 | `-p prediction:=now -p safety_margin:=0.05` | run 3 | clearance -0.004 m, 1.86 m short, solve median 32 ms, max 288 ms, late ticks 1 |

## wp4

| bag | scenario | parameters | note | result |
|---|---|---|---|---|
| wp4_N10_s3_future_1 | s3 | `-p prediction:=future -p n_horizon:=10` | run 1 | clearance +0.082 m, 0.43 m short, solve median 19 ms, max 40 ms, late ticks 0 |
| wp4_N10_s3_future_2 | s3 | `-p prediction:=future -p n_horizon:=10` | run 2 | clearance +0.049 m, goal 11.5 s, solve median 16 ms, max 52 ms, late ticks 0 |
| wp4_N10_s3_future_3 | s3 | `-p prediction:=future -p n_horizon:=10` | run 3 | clearance +0.048 m, goal 11.5 s, solve median 16 ms, max 44 ms, late ticks 0 |
| wp4_N10_s3_now_1 | s3 | `-p prediction:=now -p n_horizon:=10` | run 1 | clearance -0.006 m, 1.03 m short, solve median 15 ms, max 63 ms, late ticks 0 |
| wp4_N10_s3_now_2 | s3 | `-p prediction:=now -p n_horizon:=10` | run 2 | clearance -0.006 m, 1.03 m short, solve median 15 ms, max 72 ms, late ticks 0 |
| wp4_N10_s3_now_3 | s3 | `-p prediction:=now -p n_horizon:=10` | run 3 | clearance -0.007 m, 1.01 m short, solve median 16 ms, max 80 ms, late ticks 0 |
| wp4_N10_s4_fit_1 | s4 | `-p goal_estimate:=fit -p noise_seed:=1 -p n_horizon:=10` | seed 1 | within 0.2 m at 15.1 s, mean last 5 s 0.228 m, solve median 13 ms, max 17 ms, late ticks 0 |
| wp4_N10_s4_fit_2 | s4 | `-p goal_estimate:=fit -p noise_seed:=2 -p n_horizon:=10` | seed 2 | within 0.2 m at 13.9 s, mean last 5 s 0.212 m, solve median 14 ms, max 17 ms, late ticks 0 |
| wp4_N10_s4_fit_3 | s4 | `-p goal_estimate:=fit -p noise_seed:=3 -p n_horizon:=10` | seed 3 | within 0.2 m at 14.0 s, mean last 5 s 0.214 m, solve median 14 ms, max 19 ms, late ticks 0 |
| wp4_N10_s4_hold_1 | s4 | `-p goal_estimate:=hold -p noise_seed:=1 -p n_horizon:=10` | seed 1 | within 0.2 m at never, mean last 5 s 0.290 m, solve median 14 ms, max 18 ms, late ticks 0 |
| wp4_N10_s4_hold_2 | s4 | `-p goal_estimate:=hold -p noise_seed:=2 -p n_horizon:=10` | seed 2 | within 0.2 m at never, mean last 5 s 0.315 m, solve median 13 ms, max 19 ms, late ticks 0 |
| wp4_N10_s4_hold_3 | s4 | `-p goal_estimate:=hold -p noise_seed:=3 -p n_horizon:=10` | seed 3 | within 0.2 m at never, mean last 5 s 0.311 m, solve median 14 ms, max 22 ms, late ticks 0 |
| wp4_N20_s3_future_1 | s3 | `-p prediction:=future -p n_horizon:=20` | run 1 | clearance +0.050 m, goal 11.5 s, solve median 35 ms, max 84 ms, late ticks 0 |
| wp4_N20_s3_future_2 | s3 | `-p prediction:=future -p n_horizon:=20` | run 2 | clearance +0.049 m, goal 11.5 s, solve median 36 ms, max 95 ms, late ticks 0 |
| wp4_N20_s3_future_3 | s3 | `-p prediction:=future -p n_horizon:=20` | run 3 | clearance +0.049 m, goal 11.4 s, solve median 37 ms, max 94 ms, late ticks 0 |
| wp4_N20_s3_now_1 | s3 | `-p prediction:=now -p n_horizon:=20` | run 1 | clearance -0.007 m, 1.05 m short, solve median 33 ms, max 180 ms, late ticks 2 |
| wp4_N20_s3_now_2 | s3 | `-p prediction:=now -p n_horizon:=20` | run 2 | clearance -0.030 m, 1.19 m short, solve median 33 ms, max 173 ms, late ticks 4 |
| wp4_N20_s3_now_3 | s3 | `-p prediction:=now -p n_horizon:=20` | run 3 | clearance -0.007 m, 1.15 m short, solve median 32 ms, max 260 ms, late ticks 2 |
| wp4_N20_s4_fit_1 | s4 | `-p goal_estimate:=fit -p noise_seed:=1 -p n_horizon:=20` | seed 1 | within 0.2 m at 11.4 s, mean last 5 s 0.178 m, solve median 23 ms, max 28 ms, late ticks 0 |
| wp4_N20_s4_fit_2 | s4 | `-p goal_estimate:=fit -p noise_seed:=2 -p n_horizon:=20` | seed 2 | within 0.2 m at 10.4 s, mean last 5 s 0.166 m, solve median 23 ms, max 27 ms, late ticks 0 |
| wp4_N20_s4_fit_3 | s4 | `-p goal_estimate:=fit -p noise_seed:=3 -p n_horizon:=20` | seed 3 | within 0.2 m at 14.0 s, mean last 5 s 0.207 m, solve median 23 ms, max 28 ms, late ticks 0 |
| wp4_N20_s4_hold_1 | s4 | `-p goal_estimate:=hold -p noise_seed:=1 -p n_horizon:=20` | seed 1 | within 0.2 m at never, mean last 5 s 0.290 m, solve median 25 ms, max 32 ms, late ticks 0 |
| wp4_N20_s4_hold_2 | s4 | `-p goal_estimate:=hold -p noise_seed:=2 -p n_horizon:=20` | seed 2 | within 0.2 m at never, mean last 5 s 0.337 m, solve median 25 ms, max 33 ms, late ticks 0 |
| wp4_N20_s4_hold_3 | s4 | `-p goal_estimate:=hold -p noise_seed:=3 -p n_horizon:=20` | seed 3 | within 0.2 m at never, mean last 5 s 0.304 m, solve median 25 ms, max 31 ms, late ticks 0 |
| wp4_N30_s3_future_1 | s3 | `-p prediction:=future -p n_horizon:=30` | run 1 | clearance +0.066 m, goal 11.6 s, solve median 54 ms, max 228 ms, late ticks 7 |
| wp4_N30_s3_future_2 | s3 | `-p prediction:=future -p n_horizon:=30` | run 2 | clearance +0.052 m, goal 11.4 s, solve median 54 ms, max 130 ms, late ticks 3 |
| wp4_N30_s3_future_3 | s3 | `-p prediction:=future -p n_horizon:=30` | run 3 | clearance +0.065 m, goal 11.6 s, solve median 54 ms, max 190 ms, late ticks 4 |
| wp4_N30_s3_now_1 | s3 | `-p prediction:=now -p n_horizon:=30` | run 1 | clearance -0.009 m, 0.68 m short, solve median 48 ms, max 493 ms, late ticks 9 |
| wp4_N30_s3_now_2 | s3 | `-p prediction:=now -p n_horizon:=30` | run 2 | clearance -0.008 m, 0.83 m short, solve median 47 ms, max 579 ms, late ticks 4 |
| wp4_N30_s3_now_3 | s3 | `-p prediction:=now -p n_horizon:=30` | run 3 | clearance -0.003 m, 1.34 m short, solve median 48 ms, max 289 ms, late ticks 9 |
| wp4_N30_s4_fit_1 | s4 | `-p goal_estimate:=fit -p noise_seed:=1 -p n_horizon:=30` | seed 1 | within 0.2 m at 8.6 s, mean last 5 s 0.137 m, solve median 32 ms, max 48 ms, late ticks 0 |
| wp4_N30_s4_fit_2 | s4 | `-p goal_estimate:=fit -p noise_seed:=2 -p n_horizon:=30` | seed 2 | within 0.2 m at 12.6 s, mean last 5 s 0.199 m, solve median 32 ms, max 49 ms, late ticks 0 |
| wp4_N30_s4_fit_3 | s4 | `-p goal_estimate:=fit -p noise_seed:=3 -p n_horizon:=30` | seed 3 | within 0.2 m at 10.8 s, mean last 5 s 0.177 m, solve median 31 ms, max 48 ms, late ticks 0 |
| wp4_N30_s4_hold_1 | s4 | `-p goal_estimate:=hold -p noise_seed:=1 -p n_horizon:=30` | seed 1 | within 0.2 m at never, mean last 5 s 0.368 m, solve median 39 ms, max 52 ms, late ticks 0 |
| wp4_N30_s4_hold_2 | s4 | `-p goal_estimate:=hold -p noise_seed:=2 -p n_horizon:=30` | seed 2 | within 0.2 m at never, mean last 5 s 0.344 m, solve median 37 ms, max 50 ms, late ticks 0 |
| wp4_N30_s4_hold_3 | s4 | `-p goal_estimate:=hold -p noise_seed:=3 -p n_horizon:=30` | seed 3 | within 0.2 m at never, mean last 5 s 0.380 m, solve median 36 ms, max 47 ms, late ticks 0 |
| wp4_N40_s3_future_1 | s3 | `-p prediction:=future -p n_horizon:=40` | run 1 | clearance +0.047 m, goal 11.1 s, solve median 73 ms, max 272 ms, late ticks 10 |
| wp4_N40_s3_future_2 | s3 | `-p prediction:=future -p n_horizon:=40` | run 2 | clearance +0.045 m, goal 11.0 s, solve median 70 ms, max 253 ms, late ticks 11 |
| wp4_N40_s3_future_3 | s3 | `-p prediction:=future -p n_horizon:=40` | run 3 | clearance +0.067 m, 0.20 m short, solve median 73 ms, max 194 ms, late ticks 10 |
| wp4_N40_s3_now_1 | s3 | `-p prediction:=now -p n_horizon:=40` | run 1 | clearance -0.011 m, 1.00 m short, solve median 64 ms, max 847 ms, late ticks 15 |
| wp4_N40_s3_now_2 | s3 | `-p prediction:=now -p n_horizon:=40` | run 2 | clearance -0.013 m, 0.92 m short, solve median 62 ms, max 541 ms, late ticks 17 |
| wp4_N40_s3_now_3 | s3 | `-p prediction:=now -p n_horizon:=40` | run 3 | clearance -0.023 m, 1.02 m short, solve median 64 ms, max 325 ms, late ticks 13 |
| wp4_N40_s4_fit_1 | s4 | `-p goal_estimate:=fit -p noise_seed:=1 -p n_horizon:=40` | seed 1 | within 0.2 m at 7.6 s, mean last 5 s 0.103 m, solve median 40 ms, max 120 ms, late ticks 1 |
| wp4_N40_s4_fit_2 | s4 | `-p goal_estimate:=fit -p noise_seed:=2 -p n_horizon:=40` | seed 2 | within 0.2 m at 7.9 s, mean last 5 s 0.107 m, solve median 40 ms, max 91 ms, late ticks 0 |
| wp4_N40_s4_fit_3 | s4 | `-p goal_estimate:=fit -p noise_seed:=3 -p n_horizon:=40` | seed 3 | within 0.2 m at 7.3 s, mean last 5 s 0.165 m, solve median 40 ms, max 62 ms, late ticks 0 |
| wp4_N40_s4_hold_1 | s4 | `-p goal_estimate:=hold -p noise_seed:=1 -p n_horizon:=40` | seed 1 | within 0.2 m at never, mean last 5 s 0.328 m, solve median 48 ms, max 61 ms, late ticks 0 |
| wp4_N40_s4_hold_2 | s4 | `-p goal_estimate:=hold -p noise_seed:=2 -p n_horizon:=40` | seed 2 | within 0.2 m at never, mean last 5 s 0.350 m, solve median 49 ms, max 61 ms, late ticks 0 |
| wp4_N40_s4_hold_3 | s4 | `-p goal_estimate:=hold -p noise_seed:=3 -p n_horizon:=40` | seed 3 | within 0.2 m at never, mean last 5 s 0.444 m, solve median 48 ms, max 60 ms, late ticks 0 |

Not used: `wp0/failed_no_tb3_env/` (two empty bags, the launch could not find turtlebot3_gazebo).

## final_demo_bags

The four demo recordings of 2 Nov 2026, made by hand with the Gazebo window and RViz open
(`2026-11-02-final-recording-runsheet.md`). Demo bags: no number in the report comes from them. Locally
in `project/bags/final_demo_bags/`; the videos of the same names are in `project/videos/final_demo/`.
Results from `final-demo-takes.txt`.

| bag | scenario | parameters | note | result |
|---|---|---|---|---|
| s3_future | s3 | `-p prediction:=future` | default, `gui:=true rviz:=true` | clearance +0.053 m, goal 11.5 s |
| s3_now | s3 | `-p prediction:=now` | default, `gui:=true rviz:=true` | clearance -0.007 m, 0.92 m short |
| s4_fit | s4 | `-p goal_estimate:=fit -p noise_seed:=1` | default, `gui:=true rviz:=true` | within 0.2 m at 10.0 s, mean last 5 s 0.159 m |
| s4_hold | s4 | `-p goal_estimate:=hold -p noise_seed:=1` | node killed 8 s late; 15.5 s window | never within 0.2 m, mean last 5 s 0.322 m |
