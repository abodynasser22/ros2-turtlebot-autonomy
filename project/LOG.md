# Project log

Newest entry at the bottom. What was done, what was decided, what went wrong.

---

## 2026-10-15: planning, skeleton, copy of Lab 2

### Decisions (planning interview with Dominic)

| # | Decision | Why |
|---|---|---|
| Q1 | New package `project/ros2_ws/src/r7021e_project`. Lab 2 code copied, not moved. | Lab 2 is graded and must still run as submitted. |
| Q2 | Plank 0.50 x 0.20 m, long axis along the heading, three discs at -0.167 / 0 / +0.167 m, r = 0.130. Single-disc baseline r = 0.269. | A plank across the heading cannot pass a 0.30 m gap under any model. Three is the smallest n that fits 0.30: two discs need 0.32 m. |
| Q3 | Plank centred on the wheel axle (`base_footprint`, the `/odom` point). | Symmetric offsets, simplest equations. |
| Q4 | Plank has collision in Gazebo, mounted above the lidar. Clearance comes from ground-truth pose against the exact rectangle. | Grading the disc model with discs would be circular. |
| Q5 | Box bounds become 4 soft `set_nl_cons` on the axle point, shrunk by 0.269. | Hard bounds on a measured state deadlocked Lab 2 task 4. |
| Q6 | `n_horizon` measured at the desk: N in {20, 40, 60}, largest with p95 solve < 50 ms. One default, in the node. | Constraints scale with discs x obstacles x N. Lab 2 had 100 in the node and 20 in the launch file. |
| Q7 | Two gates before new code: (1) copied node reproduces Lab 2 in Gazebo, (2) plank model loads and drives. | Each later failure has one suspect. |
| Q8 | `SCENARIOS` table plus a separate `footprint:=one\|three` parameter. | Footprint is the independent variable. |
| Q9 | Scenario 1: circle r 0.8 with obstacle (0, 0.62, 0.12), then a figure-8 with an obstacle by the crossing. | With no obstacle the footprint is in no constraint and the pair shows nothing. |
| Q10 | Scenario 2: corridor walls plus two posts r 0.10, gap 0.60 / 0.50 / 0.40 / 0.34 / 0.30 / 0.28. "Pass" = goal reached and true clearance > 0. | Free posts let the robot drive around them, so reach would leak into the result. |
| Q11 | Claude writes the code. Dominic studies `STUDY/Project Theory Guide.html` now and a full study guide after, and runs every ROS command. | Time after Lab 4. |
| Q12 | `project_sim.launch.py` starts Gazebo, the world, the plank Burger and the bridges: the sim's equivalent of `turtlebot3_bringup`. The MPC node runs in its own terminal. | Same two-step habit as on the robot. |
| Q13 | One `SCENARIOS` dict in `mpc_node.py`, and the launch file imports it. `scenario:=s2_030` is typed in both terminals. | One copy of the numbers. Lab 2's plot tool bug was two copies. |
| Q14 | Plan as if solo. Abdalrahman owns evaluation and report on paper. | See the conversation of 15 Oct. |

### Facts found while planning

- `odom` pose = `base_footprint` = wheel axle centre. The Burger chassis box is centred at x = -0.032 and its rear corners are 0.124 m from the axle. Lab 2's 0.105 disc under-inflated the body by about 19 mm.
- Lidar top is at about 0.19 m, so the plank goes above 0.20 m.
- do-mpc soft constraints add slack linearly (`+ penalty * eps`), which is an exact penalty: slack is zero whenever a feasible plan exists and the penalty beats the multiplier.
- There is no `lab2/LOG.md`. Lab 2's log is `lab2/report_notes.md` plus findings 7a-7e in `lab2/PLAN.md`.

### What was built

| File | From | Changed |
|---|---|---|
| `ros2_ws/src/r7021e_project/r7021e_project/mpc_node.py` | `lab2/.../mpc_controller.py` | docstring package name only |
| `ros2_ws/src/r7021e_project/rviz/project.rviz` | `lab2/.../rviz/lab2.rviz` | none |
| `ros2_ws/src/r7021e_project/package.xml`, `setup.cfg` | Lab 2 | package name |
| `ros2_ws/src/r7021e_project/setup.py` | new | installs rviz/, launch/, worlds/ by glob |
| `desk/sim_scenario.py` | `lab2/plots/sim_task.py` | node path |
| `analysis/plot_run.py` | `lab2/plots/plot_rosbag.py` | node path |

### Gate 0 (desk, no ROS): passed

`python3 desk/sim_scenario.py --task 4 --laps 1` on the copied node:

| | Lab 2 report notes | copy |
|---|---|---|
| obstacle closest | 0.2249 m | 0.2249 m |
| mean error after drive-on | 0.0025 m | 0.0026 m |
| max error after drive-on | 0.0463 m | 0.0463 m |
| solver failures | 0 | 0 |

The copy behaves like Lab 2 (one lap here, two laps in the notes). Next is gate 1 in Gazebo, run by Dominic: see `RUNSHEET.md`.

---

## 2026-10-15 (evening): gate 1 results, the project node, scenarios 1 and 2

Dominic ran gate 1 and then handed over for the rest of the day. Claude ran Gazebo headless on
`ROS_DOMAIN_ID=99` with its own `GZ_PARTITION`, so nothing touched Dominic's terminals.

### Gate 1 (Dominic's bags)

| bag | result | why |
|---|---|---|
| `gate1_t4` | **pass**. About two laps (10.13 m), closest approach 0.2195 m to the 0.225 keep-out (5.5 mm of soft slack), mean circle error 4.4 mm | The copy behaves like Lab 2. |
| `gate1_t3` | fail: robot never moved | Every `/cmd_vel` was exactly zero and `/mpc_prediction` had 0 messages, so the node never had a goal. The robot sat at (0.8, 0), where t4 left it, until Gazebo restarted at 83 s. |
| `gate1_t3-version2` | fail: same | Sat at the origin for 163 s, all-zero commands. |

`/new_position` is missing from both t3 bags, so the recorder never saw a goal publisher. The goal was
published either before the node was up (`ros2 topic pub` messages are not stored, so a late
subscriber never sees them) or from a terminal on a different `ROS_DOMAIN_ID` (trap 1).
**Reproduced:** with the goal published 10 s *after* the node started, the same node and
command drove to (1.78, 0.01). Task 3 also solves at the desk with N=20 (0 failures, 8.3 s).
So it was the order of operations, not the code. Project scenarios with a point goal now carry
the goal in `SCENARIOS`, so no project run depends on publish timing.

### RViz "showed nothing of the robot"

The Lab 2 RViz config has no RobotModel display and nothing that draws the body. It only has TF
axes, Odometry arrows, scan, obstacle markers and the predicted path. Fixed in
`rviz/project.rviz`: a RobotModel display (from `/robot_description`), plus a MarkerArray on
the new `/mpc_footprint` topic, where the node draws the plank and the discs it believes in at
the measured pose. Verified headless (RViz window captured): with the new config RViz shows the
Burger, plank, discs, posts and walls, both with and without `use_sim_time`, so sim time was
**not** the cause. The likeliest cause is the missing body display. A terminal on another
`ROS_DOMAIN_ID` (trap 1) would also show an empty RViz, and the bags can't tell the two apart.
`use_sim_time:=true` stays in the RUNSHEET because it's correct in sim, not because it fixes this.

### Decisions made without Dominic (blocker rule: course tools only, proposal goals only)

| # | Decision | Why |
|---|---|---|
| D1 | **N = 20 stays** (reach 0.44 m). Q6's rule applied on a quiet machine: N=20 p95 59 ms (s2_030 three), N=40 p95 174 ms, N=60 p95 367 ms. | Only N=20 keeps the p95 inside the 100 ms tick. The first sweep read 100+ ms even for Lab 2's own task, because Dominic's Gazebo GUI was still open: **the GUI roughly triples solve time.** Timed runs use `gui:=false`. |
| D2 | s1b obstacle moved from (0, 0.25) to **(0, 0.36), r 0.08**. | At (0, 0.25) the robot's start (the origin) was inside the one-disc keep-out (0.349 m). At 0.36 both start outside, three discs need no detour, and one disc needs about 9 cm. |
| D3 | Box is `(x_min, x_max, y_min, y_max)`, not a single ±B. | The scenario 2 corridor is long in x and narrow in y. A square box can't describe it. Same four soft constraints as Q5. |
| D4 | Footprint `burger` (one disc, 0.105) kept, beside `one` and `three`. | So the Lab 2 tasks can still be rerun as gates with Lab 2's own body. |
| D5 | Circle runs are **one lap** (Lab 2 used two). | Halves run time. One lap passes the obstacle once, which is all the pair needs. |
| D6 | `rclpy.init(signal_handler_options=SignalHandlerOptions.NO)`. | **Bug inherited from Lab 2:** on Ctrl-C, Jazzy shut rclpy down before `finally: node.stop()`, the zero command failed with "publisher's context is invalid", and the robot kept its last command. Seen in the first headless run. Now Ctrl-C arrives as a plain KeyboardInterrupt, `stop()` publishes, and then rclpy shuts down. |
| D7 | Ground truth from Gazebo's PosePublisher plugin on the robot model, bridged to `/ground_truth` (PoseStamped). | One plugin and one bridge argument. The controller never subscribes to it. |
| D8 | Desk folder kept out of git: `project/.gitignore` → `desk/`, like `lab4/.gitignore`. The unpushed skeleton commit was rebuilt without `desk/sim_scenario.py`. | Dominic's instruction. |

### What was built today

- `mpc_node.py`: `FOOTPRINTS` (burger / one / three, radii from `disc_chain(n)`), `SCENARIOS`
  (lab2_t3, lab2_t4, s1a, s1b, s2_060 ... s2_028), soft box, a keep-out per obstacle per disc,
  `/mpc_footprint` markers, `/mpc_solve_time`, `rectangle_clearance()` for grading, figure-8
  reference, stop on shutdown.
- `worlds/burger_plank.sdf` (course Burger plus plank link plus ground-truth plugin) and
  `burger_bare.sdf` (Burger plus ground truth only). Both pass `gz sdf -k`. The plank inertia
  first failed validation: rounding broke ixx + iyy ≥ izz.
- `launch/project_sim.launch.py`: the sim's bringup. It imports `SCENARIOS` and spawns the
  obstacles and walls from it.
- `analysis/plot_run.py`: grades bags from ground truth against the exact rectangle, and plots a
  run or a pair.
- `desk/sim_scenario.py`: local only, gitignored.

### Scenario runs, first pass (no safety margin), and what they showed

All 16 runs recorded headless, GUI off, graded from ground truth (`analysis/plot_run.py`). These
bags are kept in `bags/margin0/` as evidence.

- **Scenario 2 matched every prediction.** One disc rejects every gap ≤ 0.50 m and stops
  1.1–1.3 m short without touching anything. Three discs pass every gap down to 0.28 m with real
  clearance (gap − 0.20)/2.
- **s1a with three discs failed.** The real plank grazed the obstacle by 2.1 mm at t = 22.4 s.
  At that moment odometry said (0.356, 0.715) and ground truth said (0.337, 0.695), 2.8 cm apart.
  The three-disc plan rode its keep-out with about 4 mm of real clearance to spare (desk
  prediction +3.7 mm), so odometry error used up the margin. The contact made the wheels slip,
  odometry then drifted **1.03 m** from truth, and the robot tracked its circle in the wrong
  place for the rest of the lap (mean path error 0.37 m).
- s1a with one disc was fine: 7.9 cm of real clearance. The big disc's waste is also its safety
  margin.

### More decisions made without Dominic

| # | Decision | Why |
|---|---|---|
| D9 | **`safety_margin` = 0.02 m** added to every keep-out (`SAFETY_MARGIN`, also a parameter). All 16 runs re-recorded with it. | The s1a graze above. Course precedent: Lab 3's `inflation_radius` 0.120 against the robot's 0.105. Cost: three discs now need 2 × (0.130 + 0.02) = **0.30 m**, and one disc 0.579 m. Desk with margin: s1a three-disc clearance +18 mm, s2_030 passes, s2_028 rejected. So the narrowest gap three discs pass becomes exactly the proposal's 0.30 m. |
| D10 | Code review fixes (`code-review` skill, 6 findings, all fixed). (1) `stop()` resets `last_cmd`, so delay compensation doesn't push the pose with a command the robot is no longer running. (2) Lab 2's "detour bigger than reach" startup warning is back. (3) Topic goals are clipped to the shrunk box. (4) "Reached in" is timed from the first non-zero command, not from bag start (12.7 s became 8.9 s, same as the desk). (5) The smoke test uses the node's N. (6) The robot entity name is one constant in the launch file. | Before the bags that count were recorded, as CLAUDE.md requires. |

### Results with the 2 cm margin (the runs that count)

16 Gazebo runs, GUI off, graded by `analysis/plot_run.py` from ground truth against the exact
rectangle. Every node shut down cleanly (no "context is invalid"). Figures are in `plots/`, and
the full tables are in `STUDY/Project Study Guide.html` §13.

**Scenario 2: narrowest gap passed: one disc 0.60 m, three discs 0.30 m.**

| gap | one disc | three discs |
|---|---|---|
| 0.60 | pass, clearance 0.200 | pass, 0.200 |
| 0.50 | stopped 1.18 m short, safe (0.150) | pass, 0.150 |
| 0.40 | stopped, safe (0.100) | pass, 0.100 |
| 0.34 | stopped, safe (0.075) | pass, 0.070 |
| 0.30 | stopped, safe (0.061) | **pass, 0.050**, the proposal's gap |
| 0.28 | stopped, safe (0.053) | stopped, safe (0.037), the margin's price |

All passes reach the goal in 8.9–9.1 s from the first command, the same as the desk.

**Scenario 1: both footprints complete both paths with no contact.**

| | path error max, one | path error max, three | real clearance, one | real clearance, three |
|---|---|---|---|---|
| s1a circle | 0.207 m | 0.075 m (2.8× less) | 0.089 m | 0.011 m |
| s1b figure-8 | 0.302 m | 0.027 m (11× less) | 0.025 m | 0.043 m |

**Solve time:** median of the per-run medians, 22 ms with one disc and 33 ms with three (1.5×).
The worst p95 was 83 ms. Everything stays inside the 100 ms tick with the GUI off.

### Where this leaves the timeline

12–19 Oct goals done in simulation: plank in Gazebo, three-disc footprint, Lab 2 tasks rerun as
gates (t4 passed; t3's failure was the goal publish, reproduced and passed), scenarios 1 and 2
with pairs. Next, 20–23 Oct: scenario 3, the obstacle centre as a TVP. Still open from today:
Dominic should rerun at least one s2 pair and s1a himself from `RUNSHEET.md` before the oral.

---

## 2026-10-21: status check, desktop reproduction, planning for the last week

### Where we stand

Scenarios 1 and 2 are done. Scenario 3 (moving obstacle) and scenario 4 (goal estimator) are not
started: the obstacle centre is still a constant in `build_TBmpc`, the launch file only spawns
static cylinders, and `plot_run.py` grades against a fixed obstacle list. There is no report,
no slides, no video and no `submission/` folder. Nothing in `project/` changed between 17 Oct and today.

### Decisions (with Dominic)

| # | Decision | Why |
|---|---|---|
| E1 | The report goes in through Canvas, due Wednesday 28 Oct (one day before the talk on Thursday 29 Oct, 11:00). Aim for Tuesday 27 Oct. | `Project Scheduling.md`, and Canvas is how the earlier labs went in. |
| E2 | Scenario 3 has a moving obstacle in Gazebo. Scenario 4 is cut if scenario 3 takes until the weekend. | Scenario 3 answers research question 2. Scenario 4 is the optional one. |
| E3 | Start `report_notes.md` now and keep it updated, in student voice. | The report draft is written from it later, as for Labs 1 to 4. |
| E4 | After scenarios 3 and 4, write a handoff for a stronger model to extend the HTML study guides. | Dominic must be able to defend all of it. |
| E5 | `slides/PRESENTATION_STRUCTURE.md` holds the structure of the Space data analysis deck. Dominic builds the final slides. | That pptx is not available to later sessions. |
| E6 | Record `/mpc_footprint` and `/mpc_obstacles` in the final bags, plus the moving obstacle's pose and the goal's pose. | The RViz replay tool reads only `/odom`, `/scan`, `/tf`, `/new_position`. Without the markers a replay shows no plank and no obstacles. |

### Reproduction on the desktop

The earlier bags are on the laptop, and `bags/` is gitignored, so none were on this machine. We
built the workspace here (`colcon build --symlink-install`, 1.5 s) and ran four runs headless on
`ROS_DOMAIN_ID=99` with their own `GZ_PARTITION`: s2_030 with three and one discs, s1a with three
and one discs. All four give the same verdicts as the laptop. Scenario 2: clearance 0.0500 m and
goal in 9.1 s with three discs, 0.0631 m and 1.314 m short with one disc. Scenario 1: clearance
0.0141 and 0.0915 m, max path error 0.0742 and 0.2207 m. Table in `report_notes.md`. Bags in
`bags/desk_check/`, not committed.

One thing that went wrong in the harness and not in the project: background jobs started by a
non-interactive shell ignore SIGINT, so `ros2 bag record` was killed before it wrote
`metadata.yaml` and the bag was unreadable. Starting each job in the foreground of a shell with
job control, or from a script that does not run in the background, fixed it. Any script that runs
the final recordings must check that `metadata.yaml` exists.

### Laptop bags regraded (from the Drive folder)

The bags are in the shared folder `R7021E-project-submission/rosbags` on the Drive. We downloaded 23 run
folders (the 16 scenario runs, the 3 gate 1 runs and the 4 zero-margin runs behind `plots/margin0/`,
about 90 MB) into `bags/` and `bags/margin0/` on the desktop, laid out as this log describes. All 16
scenario runs regrade with `plot_run.py` to the numbers in the tables above. The four zero-margin
runs give the graze again: s1a with three discs and no margin, clearance -0.0021 m, mean path error
0.371 m, odometry 1.035 m from the truth at the end. The three gate 1 bags are in `bags/` too, but
`plot_run.py` cannot grade them, because they were recorded before `/ground_truth` existed.
The desk folder (`sim_scenario.py` and `results/`) is on the Drive too and goes in `desk/`, which is
gitignored.

### Still open

Scenario 3 design (obstacle path and speed, how it moves in Gazebo, its ground truth), the laptop
bags from Drive, contributions and Abdalrahman's student ID, the Canvas brief for the report.

### Route A video test (evening of 2026-10-21) and where the work stopped

`analysis/replay_video.py` replays a bag in RViz with `rviz/replay.rviz` and records the RViz view
to an mp4 (pointer hidden, empty start trimmed). It reuses `tools/rviz_replay/rviz_replay.py` for the
window capture. The capture works on this Wayland desktop. It needs `/mpc_footprint` and
`/mpc_obstacles` in the bag, so only the `bags/desk_check/` bags work, not the laptop bags. Clips:
`videos/s2_030_three.mp4` and `videos/s2_030_one.mp4` (30 s each). In sampled frames the three-disc
plank passes between the posts, and the one-disc plank stops where the keep-out rings meet, so the
difference is visible. The clips show the plank at the odometry pose, not the ground truth. Not
checked by eye in full: smoothness and the long idle tail after the goal. Dominic judges them against
the four checks in `DEMO_PLAN.md`. For the circle, pass `--view 0 0 <scale>` to the script.
The default framing was found by trial, and RViz's Scale does not map to pixels one to one.

**Scenario 3 is not started.** Dominic approved it. Default design: a cylinder crossing the path on a
straight line at constant speed, timed so that reacting late fails. Still to do: the obstacle in
Gazebo with a ground-truth pose bridged to a topic, its centre as a TVP in `build_TBmpc` (one per
horizon step), a with-future and now-only switch, ghost markers, grading in `plot_run.py` against a
moving obstacle, and the pair runs. Then scenario 4 or a cut, the code comment pass, the report
(4 to 7 pages) and the slides draft.

---

## 2026-10-21 (night): scenarios 3 and 4 built

Dominic asked for both now, with tuning and the final recordings tomorrow.

### What was built

| File | Change |
|---|---|
| `mpc_node.py` | `SCENARIOS['s3']` (one mover) and `['s4']` (a target). `predict_mover()` and `estimate_goal()`, pure functions shared with the desk sim. `build_TBmodel(n_movers)` adds `ox<j>, oy<j>` TVPs. `build_TBmpc(..., mover_radii)` adds one soft keep-out per disc per mover against those TVPs. Node parameters `prediction` (future or now), `goal_estimate` (fit or hold), `goal_noise`, `fit_window`, `noise_seed`, `mover_margin`. The node starts the moving things on its first control tick. `/mpc_ghosts` markers. |
| `project_sim.launch.py` | `mover_sdf`, `target_sdf` (a velocity controller and a pose publisher each), `model_bridge` for `/<name>/pose` and `/<name>/cmd_vel`. |
| `analysis/plot_run.py` | Grades a moving obstacle from `/mover_1/pose` and a moving goal from `/target/pose`, against the exact rectangle. Time marks count from the first command. The moving-goal metric uses only the commanded period. Pair labels are the bag names. |
| `analysis/run_headless.py` | The headless run harness used for the desktop checks. |
| `rviz/replay.rviz`, `rviz/project.rviz` | Ghost display. `replay_video.py` plays `/mpc_ghosts` too. |
| `RUNSHEET.md` | Commands for scenarios 3 and 4. |
| `desk/sim_scenario.py` | Moving obstacle and goal, `--prediction`, `--estimate`, `--noise`. Local, gitignored. |

### Decisions

| # | Decision | Why |
|---|---|---|
| F1 | The node reads the mover's position from Gazebo and knows its velocity from `SCENARIOS`. | The proposal hands over the obstacle's future. No tracker. |
| F2 | `MOVER_MARGIN` = 0.03 m extra keep-out for a moving obstacle (keep-out 0.28 m). | With its future the controller passed at only 1 to 2 cm, a coin flip against 1 to 3 cm of odometry error. Desk clearance became +0.044 m. |
| F3 | s3 obstacle: start (1.0, 1.2), velocity (0, -0.30), r = 0.10, goal (2.0, 0.0). | Grid on the desk sim: with its future it waits and passes, without it the plank hits it. |
| F4 | s4 ball: start (1.2, -1.2), velocity (0.05, 0.20), noise 0.02 m, fit window 1.0 s, box (-0.5, 3.5, -2.5, 2.5). | The first geometry (0.12 m/s, moving away) showed no difference, the robot catches up either way. This one crosses the path and the fit gets within 0.2 m where the hold does not. |
| F5 | The pair differs in one parameter, and both pair members use the same noise seed. | One change per result. |

### First Gazebo results (headless, the numbers in `report_notes.md`)

s3: with its future real clearance +0.0512 m and goal in 11.4 s. With only its position now,
contact (-0.0063 m at 3.8 s), odometry 0.886 m off, goal not reached (0.912 m short).
s4: fit within 0.2 m at 14.0 s, closest 0.185 m, mean over the last 5 s 0.221 m. Hold never within 0.2 m,
closest 0.345 m, mean 0.375 m. Scenario 2 (s2_030, three discs) still gives +0.0499 m and 9.1 s.

### For tomorrow (tuning, then the final recordings)

1. Look at it in the Gazebo window once (`gui:=true`) and in RViz: the orange cylinder, the green ball,
   the ghosts. Nothing has been looked at on screen yet, only graded from bags.
2. Repeat s3 and s4 three times each to see the spread, and decide whether `fit_window`, `goal_noise`
   or the ball speed need changing. The Gazebo gain in s4 is smaller than at the desk.
3. Record the final bags with `analysis/run_headless.py`, including `/mpc_footprint`, `/mpc_obstacles`,
   `/mpc_ghosts` and the two pose topics, and check `metadata.yaml` in each.
4. Dominic runs s2 and s1a, then s3 and s4, by hand from `RUNSHEET.md`.
5. Then the comment pass, the study guides (Opus handoff), the report and the slides draft.

---

## 2026-10-24: tuning, repeats, documents, run sheet

Dominic asked for everything to be finished, so that from Monday only his own runs from `RUNSHEET.md`
are left. Git: he chose to leave everything uncommitted.

### The recorder, and the harness that replaced my script

`analysis/run_headless.py` replaces the bash script of 2026-10-21. Same four terminals, window off. It
resets Ctrl-C for the children, so it also works from a background shell, and it checks that
`metadata.yaml` exists. The first background batch of 2026-10-21 had lost every bag for that reason.

### A mistake, and the guard against it

The first batch of demo runs passed `--outdir` after the positional arguments. The argument parser
handed it to the node, which crashed on it, and the harness recorded the idle robot into the default
`bags/` folder after deleting any bag of the same name. That overwrote six laptop bags
(`s1a_*`, `s1b_*`, `s2_050_*`). They were restored from the Drive with the same verified download, and
regraded to the original numbers. The Study Guide had been built in that window, so it was rebuilt. The
harness now refuses to touch an existing bag unless `--overwrite` is given, and refuses options that come
after the scenario. The Drive folder `R7021E-project-submission/rosbags` is the backup of the 16 runs.

### Repeats (three each, headless, the numbers in `report_notes.md` and the study guide)

| | runs | result |
|---|---|---|
| s3 with its future | `s3_future_1..3` | pass 3 of 3, clearance +0.049, +0.048, +0.056 m, goal in 11.5, 11.4, 11.5 s |
| s3 only position now | `s3_now_1..3` | contact 3 of 3, -0.008, -0.007, -0.006 m, stopped 1.04, 0.99, 1.59 m short |
| s4 fit | `s4_fit_1..3` | within 0.2 m at 8.9, 13.9, 12.9 s, mean over the last 5 s 0.138, 0.210, 0.200 m |
| s4 hold | `s4_hold_1..3` | never within 0.2 m, mean 0.341, 0.326, 0.301 m |

Nothing needed re-tuning. The verdicts did not change between runs. `bags/demo/` holds fresh runs of
`s1a`, `s1b` and `s2_050` for the video, because the laptop bags have no marker topics.

### Decisions

| # | Decision | Why |
|---|---|---|
| G1 | No pass or fail for scenario 4. The grader prints the metrics and says to compare the pair. | A ball cannot be touched, and a PASS for the hold run was misleading. |
| G2 | The moving-goal metric covers only the time the controller was commanding. | The bag keeps recording after Ctrl-C, and a stopped robot next to a stopped ball counted as a good result. |
| G3 | Pair plot labels are the bag names. | Both runs of scenarios 3 and 4 have the same footprint, so the old label could not tell them apart. |
| G4 | `videos/` is gitignored. | Media is large and goes on the Drive, as in the root `.gitignore`. |

### Clips and the demo video

`replay_video.py` made ten clips in `videos/` from the bags (the circle and the eight at 2x), and
`make_demo_video.py` put each pair side by side with captions (`pair_<name>.mp4`) and chained the six pairs
into `videos/demo.mp4` (130 s). In scenario 3 the right clip shows the obstacle ghosts trailing down its path
and the left clip shows them stacked on one spot, and in scenario 4 the fit draws a trail of predicted
goals while the hold has one dot. They come from the desktop bags (`bags/demo/`, `s3_*_1`, `s4_*_1`) because
the laptop bags have no marker topics. `videos/` is gitignored and goes on the Drive.

### Checks that were done

Gazebo with its window (`gui:=true`) and the node and live RViz (`project.rviz`) all start without
errors on scenario 3. The smoke test solves for all five scenarios. The desktop runs of s1a, s1b and
s2_050 agree with the laptop bags: clearances within 1 cm, the same verdicts. Not looked at by eye in the
Gazebo window: that needs a person at the screen.

### Documents

- `STUDY/Project Theory Guide.html`: sections 13 and 14 are now full explanations with new diagrams
  (collision course, pursuit geometry), the least-squares derivation, the noise arithmetic
  (0.28 m/s against 0.022 m/s), decisions F1 to F5, new oral questions and glossary terms.
- `STUDY/Project Study Guide.html`: rebuilt by `build_study_guide.py`. New sections 13 and 14 (the code
  for things that move, Gazebo and grading), results of scenarios 3 and 4 generated from the bags, four new
  silent failures, new things to try, eleven new oral questions. Sections 13 to 16 became 15 to 18.
- `RUNSHEET.md`: rewritten as the Monday guide: set up once, four pairs with expected results, RViz,
  desk sim, troubleshooting, reference.
- `report_notes.md`, `DEMO_PLAN.md`, `slides/PRESENTATION_STRUCTURE.md`: brought up to date.

### Left for Dominic and for next week

Dominic runs the four pairs by hand (Monday). Then the code comment pass, the report (4 to 7 pages,
via Canvas by Wednesday 28 Oct, aim Tuesday), the slides draft and the speech manuscript, the video
upload, and `project/submission/`.

---

## 2026-10-26: audit of the documents against the bags

Dominic asked that nothing in the report or the other documents be made up, because the teacher will notice
a discrepancy. `analysis/dynamics.py` now reads the time series of the runs, and `OBSERVED.md` records what
they show. Every behavioural claim was checked against it. What was wrong, and what it was changed to:

| Claim before | What the bags show | Changed in |
|---|---|---|
| With its future the robot "waits for the obstacle to cross" | It drives straight until 1.8 s, turns, stops at x = 0.70 to 0.71 m at about 3.4 s, keeps turning in place (heading -35 degrees at 3.4 s, -61 at the crossing, -90 at 4.7 s), and drives on at about 5 s | report notes, both guides, run sheet, demo plan, video caption |
| "The contact made the wheels slip" | After the contact the true heading kept turning (300 to 550 degrees over the run) while odometry's did not. The cause was not investigated | report notes, both guides, run sheet |
| The fit "cuts across" | Both robots line up with the ball's path by 8 s. The fit trails 0.19 to 0.26 m behind, the hold 0.36 to 0.40 m | both guides, run sheet, video caption, diagram |
| "Odometry is 1 to 3 cm off" | Largest error over a run: 1.4 to 3.5 cm in scenarios 1 to 3, up to 8.0 cm in scenario 4 | report notes, both guides |
| "9.1 s with nothing in the way" | The same 2 m drive past the open 0.60 m corridor took 8.9 s. No scenario 3 run without the obstacle exists | report notes, both guides |
| The graze "at 22.4 s", odometry "2.8 cm" off | 18.6 s after the first command (22.4 s was from the bag start), 2.7 cm | report notes, study guide |
| The plank "at x = 0.9 m at 4 s" on a collision course | A robot driving straight on would be at about 0.85 m. This is a calculation, not a recording | Theory Guide |
| The fit "lags a turn by about half its window" | Not tested. Now worded as an expectation | both guides |
| Solve time in the failed runs "not investigated" | Longest while an avoidance is planned (median 53 to 72 ms between 3 and 6 s, about 30 ms otherwise). Single ticks reached 116 ms with its future and 127 to 248 ms without | report notes, study guide |
| "The 95th percentile stays inside the tick" read as "everything" | True for the 95th percentile. Single ticks exceed 100 ms | report notes |

Also checked and found consistent: the one-disc stop at x = 0.687 m against the 0.702 m the keep-out rings
predict, the real clearance of +0.048 to +0.056 m against the 0.05 m the two margins add up to, the graze
numbers, and all the repeat tables. Odometry stays within 0.5 degrees of the true heading in every run with its
future.

## 2026-10-26 (evening): report, slides draft, defence guide, submission folder

- Report built as `Project_report_group6.docx` by `make_report.py` (7 pages in a LibreOffice render, no PDF delivered). Contributions
  use Dominic's wording with the student IDs. Block diagram title is "Control stack of the project", SVG keeps its text editable.
- Found two things that disagreed with the bags and fixed them everywhere (report, OBSERVED, notes, run sheet, both guides, slides draft):
  1. The RViz clips draw the plank at the `/odom` pose. In 11 of the 12 video bags odometry is within 4.8 cm of the truth. In `s3_now_1` it is up to
     1.075 m off after the contact, so that clip seemed to reach the goal while the real run stopped 1.04 m short. The pair clip now carries a note
     and the report says so.
  2. "Turned in place by about 90 degrees so that the narrow end faced the obstacle" stated a purpose. Measured: heading -35 degrees at 3.4 s,
     -61 degrees at the crossing (3.98 s), -90 degrees at 4.7 s. The purpose is now marked as our reading, not tested.
- `slides/PRESENTATION_DRAFT.md` (13 slides plus backups) and `slides/make_script.py`, which writes `PRESENTATION_SCRIPT.md` from the
  Say blocks (about 2,520 words). Lecture links checked against the lecture PDFs (Lecture 3 non-holonomic, Lecture 4 unicycle and MPC,
  Lectures 5 to 7 map inflation, Lecture 8 Kalman, Lecture 10 least squares).
- `STUDY/Project Defence Guide.html` (built by `STUDY/build_defence_guide.py` from `defence_template.html`): blind map, ten predict-then-check
  cards, calculators, 50 questions with answers, numbers sheet. Calculated results are labelled as such. One new derived result: the
  one-disc ring geometry predicts every stopping distance in scenario 2 to within 1.0 to 1.4 cm.
- `BAGS.md` lists where the 12 demo bags are. `submission/` holds the report, code, analysis scripts, figures and a README with
  `[VIDEO LINK]` and `[BAG LINK]` to fill. No bags, no PDF.
- Left for Dominic: upload `s3_*`, `s4_*`, `demo/`, `desk_check/` to the Drive, fill the two links, generate the PDF, copy the final report
  into `submission/` again if it is edited, check the page count once in Word.
- Links filled in (video folder, bags of scenarios 1 and 2, bags of scenarios 3 and 4 and the video runs). Report top and bottom margins
  0.6 in to keep 7 pages. `~/R7021E-bags-to-upload/` (80 MB) and `~/R7021E-video-to-upload/` (`demo.mp4`) hold exactly what is not yet on the Drive.
- Bags sorted into essential and `bags/non-essential/` (see BAGS.md). Planning and study files (LOG, RUNSHEET, DEMO_PLAN, OBSERVED, BAGS, report_notes,
  grading and scheduling notes, make_report.py, STUDY/, slides/) are in `project/.gitignore` and were removed from the git index. They stay on disk.
  The earlier commit still holds LOG.md, RUNSHEET.md, Project Scheduling.md and the first two study guides (private repo).

