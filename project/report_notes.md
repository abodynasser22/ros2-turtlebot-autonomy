# Project: report notes

Source notes for the project report of group 6 (R7021E, MPC for a robot that carries a plank,
with a moving goal and a moving obstacle). Started 2026-10-21 from `LOG.md`, `RUNSHEET.md`, the
proposal (version 2), the code in `ros2_ws/src/r7021e_project/` and the 16 Gazebo runs of
2026-10-15 to 2026-10-17. Figures are in `plots/`. The run bags are in the shared Drive folder
`R7021E-project-submission/rosbags`, and the desk simulator and its results are in a second Drive
folder. `LOG.md` is the dated log of what we did. This file is the
report-facing story. Keep it updated as the work goes.

Scenarios 3 and 4 were built on 2026-10-21 and have first Gazebo results. The final numbers come from
the runs recorded after tuning. Still open: the video link and every item marked
`[PLACEHOLDER: ...]`.

## Voice, for whoever drafts the report from this

We write as two students finding out how this works. First person plural. Plain declarative
sentences, numbers with units, a literal "In words:" after an equation, failures stated first
and the cause explained, British spelling, sentence-case headings, no em dashes. Say what we
decided and why, in what order we tried things, what we dropped and the real numbers. Leave out
small slips. Only the problems that changed what we did belong in the report.

Page limit: Canvas gives none. Dominic's own target is 4 to 7 pages, with 6 to 7 as the most. Lab 1
went the same way and was cut to fit by removing figures first, then shrinking the rest, then
typography, and only then prose. Whether code and video are asked for is covered by
`Project Grading.md` (code yes, videos as evidence). The report goes in through Canvas.

## What the graders look for

From `Project Grading.md`. The report must build on the proposal, be self-contained, and carry
plots, screenshots and videos as evidence. The code is submitted too, with a short descriptive
docstring at the top of each file and comments only where something is not obvious. The grading doc
says plainly that it is fine if scope or goals changed or were not reached, as long as we show what
worked and explain which proposal components did not work and how that affected the plan. The group
part is 50 points (solution and presentation 20, methodology and evaluation 15, report 15) and the
individual part is 50 (identifiable contribution 15, technical understanding of one's own work 20,
discussion of results, limitations and learning outcomes 15). The report and the talk must name the
roles of the members. Grade boundaries: 3 from 50, 4 from 65, 5 from 85.

## Contributions

Wording from Dominic on 2026-10-21. 

1. Dominic Addo: came up with the project outline, using Lab 2's work as the basis. Discussed with
   Abdalrahman how to turn the idea into code plans and implementation details, and then worked on
   the code: the controller, the scenarios, the Gazebo worlds, the runs and the analysis.
2. Abdalrahman Nasser (abdnas-2): discussed the code plans and implementation details with Dominic, and took
   the report-writing steps, defining structure and presentation details together with Dominic.

## Block diagram

`project-block-diagram-v2.png` (and `.svg`). It shows the Gazebo world and bridge, the three new
blocks (obstacle motion model, goal estimator, body footprint), the MPC solve and the evaluation
harness. All of them are built. In the code they are: the body footprint (`FOOTPRINTS`, `disc_chain`),
the obstacle motion model (`predict_mover`), the goal estimator (`estimate_goal`), the MPC solve
(`build_TBmpc`), and the evaluation harness (`plot_run.py`). One difference from the diagram: the
obstacle and the goal come into the node as `/mover_1/pose` and `/target/pose`, with the
obstacle's velocity taken from the scenario table, and the goal's position gets 2 cm of noise added
in the node. `[PLACEHOLDER: redraw the diagram with those topic names, if it is used in the report.]`

## The problem and the two questions

In Lab 2 we built an MPC for the TurtleBot3 Burger with do-mpc. Two things in it were frozen:
the robot is one disc of 0.105 m, and every obstacle stands still. For the project we want the
robot to carry a plank of 0.50 x 0.20 m, and we want obstacles that move, because a real floor
has people and machines crossing it. A plank as one disc has a keep-out radius of 0.269 m, so
the controller would refuse a 0.30 m gap that the robot fits through. We ask two things:

1. Does describing the body as a short chain of discs let the robot use gaps that a single disc
   rejects?
2. If the controller is told where an obstacle will be, and not only where it is now, does it
   keep clear in cases where reacting late cannot?

## What we built on: the Lab 2 controller

The robot is modelled as a unicycle with state (x, y, theta) and inputs v and omega:

    x_dot = v cos(theta),   y_dot = v sin(theta),   theta_dot = omega

At every tick (0.1 s) do-mpc solves for the inputs over the next N = 20 steps that bring the
robot to the goal, and sends only the first one. The goal enters as a time-varying parameter
(TVP), one value for each step of the horizon, which we overwrite before each solve. That is how
Lab 2 handled a moving reference, and it is the mechanism we extend for the moving obstacle.
Rebuilding the solver takes seconds and a tick is 0.1 s, so a changing quantity has to be a TVP.

In words: the solver is built once. After that we only change the numbers it reads.

Obstacles are constraints, one per obstacle, written as a soft constraint with slack. The cost
of the slack is linear with weight 10^4, so the slack is zero whenever a plan that keeps clear
exists. Lab 2 showed this to 1 mm. We kept three things from Lab 2 unchanged: the delay
compensation (solve from where the robot will be when the command lands), holding the last
command for up to three failed solves, and the stop on stale odometry.

## How it connects to the lectures and labs

The grading asks for this explicitly. Candidate links from the lecture titles in
`~/r7021e_2026/docs/lectures/`, to be checked against the slides: Lecture 3 (modelling of ground
robots) for the unicycle and the fact that the robot cannot move sideways. Lecture 4 (models and
MPC) for the controller. Lectures 5 to 7 (navigation) for obstacle avoidance and the keep-out idea.
Lecture 10 (least squares) for the constant velocity fit in scenario 4, with Lecture 8 (Kalman
filter) as the alternative. Lecture 2 (ROS) for nodes, topics and bags. From the labs: Lab 2 is the
controller we copied and extended, Lab 3 gave the inflation radius that our safety margin follows
(0.120 m for a 0.105 m robot), and Lab 1 gave the unicycle model and our measurements of odometry
delay. `[PLACEHOLDER: one sentence per link, from the lecture slides.]`

## Scenarios 1 and 2: the body as discs

### Why discs, and how big

A disc gives a smooth quadratic constraint, which IPOPT handles well. A rectangle has corners and
edges where the gradient jumps. We cut the plank into n equal slices along its length and put
one disc on each slice, just big enough to cover the slice's corners:

    r_n = sqrt( (L / 2n)^2 + (W / 2)^2 ),   L = 0.50 m,   W = 0.20 m

In words: the radius is half the diagonal of one slice. It can never go below W / 2 = 0.10 m.

| n | radius | gap it needs (2 r) |
|---|---|---|
| 1 | 0.269 m | 0.538 m |
| 2 | 0.160 m | 0.320 m |
| 3 | 0.130 m | 0.260 m |

Three is the smallest n that fits the proposal's 0.30 m gap. Each extra disc adds one constraint
per obstacle per step and saves less width, so we stopped at three. The discs sit on the body
axis at -0.167, 0 and +0.167 m, centred on the wheel axle, which is the point `/odom` reports.
The plank lies along the heading. Across the heading it would present 0.50 m of width to the gap,
so it could not pass a 0.30 m gap under any model, and the robot cannot move sideways to fix that.

### The constraints

For each disc i and obstacle j the keep-out constraint is

    (r_obstacle + r_disc + margin)^2 - ((c_i,x - o_j,x)^2 + (c_i,y - o_j,y)^2) <= 0
    c_i,x = x + d_i cos(theta),   c_i,y = y + d_i sin(theta)

In words: every disc centre must stay farther from the obstacle's centre than the two radii plus
a small margin. The disc centres turn with the heading, so each one is a short expression in x,
y and theta. Both sides are squared, so there is no square root.

The boundary box is four soft constraints on the axle point, shrunk by 0.269 m, the radius the
plank sweeps when the robot turns on the spot. In Lab 2 a hard bound on a measured state made
step zero infeasible when odometry put the robot outside, and task 4 never ran on the robot
because of it. Soft constraints cannot deadlock that way.

### The horizon

We measured N on a quiet machine with the Gazebo window closed, on the hardest scenario (s2_030,
three discs). The 95th percentile of the solve time was 59 ms at N = 20, 174 ms at N = 40 and 367 ms
at N = 60. Only N = 20 stays inside the 100 ms tick. Its reach is 20 x 0.1 s x 0.22 m/s = 0.44 m,
which is enough because every detour in scenarios 1 and 2 is under 0.2 m. The Gazebo window
roughly triples the solve time, so every run that counts was recorded headless.

### The safety margin

Our first runs had no margin. In s1a the three-disc plank grazed the obstacle by 2.1 mm, 18.6 s after
the first command. At that moment odometry said (0.356, 0.715) and the ground truth said (0.337, 0.695),
2.7 cm apart, and the desk simulation had predicted a clearance of only +3.7 mm. After the graze odometry
drifted away from the truth, 0.22 m at 25 s and 1.03 m at the end of the lap, and the robot followed its
circle in the wrong place for the rest of the lap (mean path error 0.37 m). We did not test why the drift
started. We added 0.02 m to every keep-out. Lab 3 did the same with an inflation radius of 0.120 m for a
0.105 m robot. The price is 4 cm of gap: three discs now need 2 x (0.130 + 0.02) = 0.30 m and one disc
0.579 m, so the 0.28 m gap is
rejected. The narrowest gap that three discs pass is now exactly the proposal's 0.30 m.

## How we check a run

The controller believes in discs and the world contains a rectangle. If we graded a run with disc
distances we would be asking the model whether the model was right. So we grade from Gazebo's
ground-truth pose of the robot, bridged to `/ground_truth`, against the exact 0.50 x 0.20 m
rectangle. The controller never reads `/ground_truth`. The clearance is

    p = R(theta)^T (o - (x, y)),   q = clamp(p, plank half sizes),   clearance = |p - q| - r_obstacle

In words: move the obstacle centre into the plank's own frame, find the nearest point of the
rectangle, and take the distance between the surfaces. A value of 0 or less is contact. A scenario 2
run passes when the goal is reached and the true clearance stays above 0. `analysis/plot_run.py`
does this from a bag, and every run is saved so the numbers can be rechecked without Gazebo.

## Results of scenarios 1 and 2

16 Gazebo runs, GUI off, graded from ground truth, with the 2 cm margin. Figures:
`plots/s2_050_pair.png`, `plots/s2_028_pair.png`, `plots/s1a_pair.png`, `plots/s1b_pair.png`.

Scenario 2, corridor with two posts of r = 0.10 m at x = 1.0 m, goal at (2.0, 0.0):

| gap | one disc | three discs |
|---|---|---|
| 0.60 m | pass, clearance 0.200 m | pass, 0.200 m |
| 0.50 m | stopped 1.18 m short, safe (0.150 m) | pass, 0.150 m |
| 0.40 m | stopped, safe (0.100 m) | pass, 0.100 m |
| 0.34 m | stopped, safe (0.075 m) | pass, 0.070 m |
| 0.30 m | stopped, safe (0.061 m) | pass, 0.050 m |
| 0.28 m | stopped, safe (0.053 m) | stopped, safe (0.037 m) |

The narrowest gap passed is 0.60 m with one disc and 0.30 m with three. At 0.50 m the real plank
has 0.15 m to spare on each side and the one-disc controller still refuses, because its model of
the body does not fit. It drives up to where its 0.389 m keep-outs meet on the centre line and
stops there. The goal cost pulls it forward, the slack cost forbids it, and the box forbids going
round, so that is a local minimum. It is what a controller that believes it does not fit should do.
Every pass reaches the goal in 8.9 to 9.1 s from the first command, the same as the desk run.

Scenario 1, known path with one obstacle, both footprints complete both paths without contact:

| | max path error, one disc | max path error, three discs | real clearance, one | real clearance, three |
|---|---|---|---|---|
| s1a circle, r = 0.8 m | 0.207 m | 0.075 m (2.8 times less) | 0.089 m | 0.011 m |
| s1b figure of eight | 0.302 m | 0.027 m (11 times less) | 0.025 m | 0.043 m |

The three-disc body leaves its path far less, because its keep-out is smaller. The price is
clearance: three discs spend the room that one disc wasted, and that room was also what absorbed
odometry error. This is why the margin is there.

Solve time, median of the per-run medians: 22 ms with one disc and 33 ms with three, 1.5 times
more and not 3 times, because IPOPT's cost does not grow in proportion to the number of
constraints. The worst 95th percentile was 83 ms, inside the 100 ms tick.

We repeated four of these runs on a second machine to check the numbers hold. See the section
"Reproduction on the desktop" near the end.

## Scenario 3: the moving obstacle

### What we built

A cylinder of r = 0.10 m crosses the robot's path on a straight line at a constant speed. It
starts at (1.0, 1.2) and moves at (0, -0.30) m/s, so it reaches the robot's line (y = 0) after
4.0 s. The robot starts at the origin and drives to (2.0, 0.0), and by 4 s it is at about
x = 0.9 m, so the two are on a collision course. In Gazebo the cylinder is a heavy body (50 kg)
with a velocity controller, so it keeps the velocity it is given. Its true pose comes out of
Gazebo at 30 Hz on `/mover_1/pose`. The controller node starts the obstacle on its first control
tick, so the obstacle and the robot start together in both runs of a pair.

### What changes in the controller

The obstacle centre becomes a time-varying parameter, one value per horizon step, written before
every solve exactly as the goal is. For each disc i, each moving obstacle and each step k:

    (r_o + m + r_d + margin)^2 - ((c_i,x - o_x(k))^2 + (c_i,y - o_y(k))^2) <= 0
    o(k) = o_now + v (d + k) dt     with its future
    o(k) = o_now                    with only its position now

In words: the keep-out is the same as for a still obstacle, but the centre it is measured from is
where the obstacle will be at step k. d is the one tick of delay that the controller already
compensates for. With its future the controller sees the crossing coming: in our runs it first
reacted at 1.8 s, 2.2 s before the obstacle crossed its line, which is close to the 2.0 s horizon. With
only its position now, the obstacle looks still, and it first reacted at 3.2 s, when the obstacle was
0.24 m from the line. The two runs differ in one parameter, `prediction`.

We read the obstacle's position from Gazebo and we know its velocity because we chose its path.
That is the assumption in the proposal. A real robot would need a tracker for both.

We gave the moving obstacle 0.03 m more keep-out than a still one (m above). In the desk runs the
controller that knows the future passed with only 1 to 2 cm of real clearance. Odometry was 1.4 to
3.5 cm off the ground truth in scenarios 1 to 3 (the largest error over a run), so that would have
been a coin flip. It is the same reasoning as the 2 cm margin. The keep-out is now 0.28 m. In Gazebo the
real clearance with its future came out at +0.048 to +0.056 m, which is the 0.05 m that the two margins
(0.02 m and 0.03 m) add up to: the controller passes about as close as the constraint lets it.

The node also draws ghosts on `/mpc_ghosts`: the obstacle where the controller believes it will be
at steps 0, 5, 10, 15 and 20. With its future they run along the path. Held at now, they sit on
one spot. This is the picture that explains the idea.

### Results

Three runs of each, headless Gazebo, graded from the ground truth of the plank and of the obstacle at
the same instants. The runs of one mode have the same settings. Their small differences come from the
simulator's timing, which we did not control.

| run | with its future | only its position now |
|---|---|---|
| 1 | clearance +0.049 m, goal in 11.5 s | contact, -0.008 m at 3.7 s, stopped 1.04 m short |
| 2 | clearance +0.048 m, goal in 11.4 s | contact, -0.007 m at 3.8 s, stopped 0.99 m short |
| 3 | clearance +0.056 m, goal in 11.5 s | contact, -0.006 m at 3.8 s, stopped 1.59 m short |
| odometry against truth at the end | 0.02 to 0.04 m | 1.0 to 1.6 m |

With its future the controller passed three times out of three, and with only the position now it
touched the obstacle three times out of three, by 6 to 8 mm for 0.5 to 0.7 s. The desk simulation had
predicted +0.044 m and -0.041 m. The desk has no physics, so nothing stops the plank from passing through
the obstacle there, but the verdicts agree.

What the robot did with its future: it drove straight at 0.22 m/s until 1.8 s, then began to turn
clockwise, braked to a stop at x = 0.70 to 0.71 m at about 3.4 s, and kept turning in place: the heading was
-61 degrees when the obstacle crossed the robot's line at 3.98 s (with 0.08 to 0.09 m of clearance) and -90 degrees
at 4.7 s, which puts the plank along the obstacle's direction of travel. The robot then turned back and drove on, with its speed above
0.2 m/s again at 5.3 s in two runs and at 4.5 s in the third, and reached the goal in 11.4 to 11.5 s. The same
2 m drive takes 8.9 s past the open 0.60 m corridor of scenario 2, so the manoeuvre cost about 2.5 s.
Odometry agreed with the truth to within 0.5 degrees of heading.

What it did with only the position now: it drove straight until 3.2 s, when the obstacle was 0.24 m from its
line, braked and began to turn, and the plank touched the obstacle at 3.5 s. After that the true heading kept
turning clockwise, by 300 to 550 degrees over the run, while odometry did not follow it, so the controller
steered from a pose that was wrong by about a metre. The robot ended 1.0 to 1.6 m from where odometry placed
it, and 1.0 to 1.6 m short of the goal. We do not know why the true heading kept turning after the obstacle
had gone, and we did not test whether the wheels slipped. The symptom is the same as in the zero-margin graze
of scenario 1: after a contact, odometry no longer agrees with the truth. That is why the real distance
comes from the ground truth.

The solve time was longest while the avoidance was being planned: a median of 53 ms between 3 and 6 s with
its future and 60 to 72 ms without, against about 30 ms in the rest of the run. The 95th percentile over a
run was 60 to 66 ms with its future and 88 to 94 ms without. Single ticks reached 116 ms with its future and
127 to 248 ms without, which is more than the 100 ms control tick.

Figure: `plots/s3_pair.png`, made by `plot_run.py`. Bags: `bags/s3_future_1` to `3` and `bags/s3_now_1` to `3`.

## Scenario 4: the estimated goal

### What we built

The goal is a small green ball with no collision, moving at a constant velocity. It starts at
(1.2, -1.2) and moves at (0.05, 0.20) m/s, so it crosses in front of the robot at close to the
robot's top speed. The controller never gets its true position. At every tick it sees the ball's
position plus Gaussian noise of 2 cm, and it keeps the last 1.0 s of those (10 samples). The true
pose goes to the bag on `/target/pose` for the evaluation. The node starts the ball on its first
tick, like the moving obstacle.

### The two estimators

With `goal_estimate:=fit` the node fits a constant velocity to the last observed positions by least
squares, one line per axis, and extends it across the horizon:

    v = sum((t_m - t_mean)(p_m - p_mean)) / sum((t_m - t_mean)^2)
    g(k) = p_fit(t) + v (d + k) dt

In words: v is the slope of the best straight line through position against time, and the goal at
step k is where that line will be. Fitting over several points averages the noise out, whereas
differencing the last two points would multiply it by 1 / dt. With `goal_estimate:=hold` the goal
is the latest observed position for every step. The two runs use the same noise seed.

### What we tried first, and the geometry that works

Our first ball moved slowly away from the robot at 0.12 m/s. In the desk simulation the fit and the
hold gave almost the same result, 0.27 against 0.29 m, because the robot is faster than the ball
and catches up whatever the controller believes. The ball also left the box by the end of the run.
So the geometry decides whether a prediction matters. We changed the ball to cross the robot's path
at 0.21 m/s. In the desk simulation the fit then gets within 0.2 m of it after 8.6 s and the hold
never does.

### Results

Three runs of each, headless Gazebo, with noise seeds 1, 2 and 3, the same for the two modes. The
distance is the ground-truth robot against the ground-truth ball, over the time the controller was
commanding.

| noise seed | fit: first within 0.2 m | fit: mean over last 5 s | hold: first within 0.2 m | hold: mean over last 5 s |
|---|---|---|---|---|
| 1 | 8.9 s | 0.138 m | never | 0.341 m |
| 2 | 13.9 s | 0.210 m | never | 0.326 m |
| 3 | 12.9 s | 0.200 m | never | 0.301 m |
| mean | | 0.183 m | | 0.323 m |

The fit got within 0.2 m of the ball in every run, and the hold never did. The mean distance over the
last 5 s is about 43 percent smaller with the fit. The noise seed changes the fit's result (0.14 to 0.21 m),
because a different noise sample gives a different fitted line, and it did not change the ordering.

How the two differ: both robots drove at the speed limit of 0.22 m/s for 99 percent of the run and
reached the turn-rate limit of 0.8 rad/s, and the ball moves at 0.206 m/s, so the robot is only 7 percent
faster. By 8 s both had lined up with the ball's path (sideways offset 0.08 to 0.11 m) and trailed behind it.
What differs is how far behind. Along the ball's path, the fit was 0.19 to 0.26 m behind at 8 s and 0.10 to
0.18 m at 15 s. The hold was 0.36 to 0.40 m behind at 8 s and 0.27 to 0.31 m at 15 s. After 8 s both closed
the gap by only about 0.01 m/s, which is what a 7 percent speed margin allows. So the gain from the fit is
a smaller lag, not a different path.

The desk simulation predicted 0.142 m for the fit and 0.313 m for the hold. In Gazebo the fit is a little
worse (0.183 m) and the hold almost the same (0.323 m). The desk robot has no acceleration limit and no
odometry error, which may explain the difference, but we did not isolate it. Odometry was up to 8 cm off
the truth in the fit runs and up to 4.6 cm in the hold runs. The 95th percentile of the solve time was
26 to 31 ms, well inside the tick.

Figure: `plots/s4_pair.png`. Bags: `bags/s4_fit_1` to `3` and `bags/s4_hold_1` to `3`.

What this does not show: the ball moves in a straight line at a constant speed, so a constant
velocity model is exact for it. A ball that turned would show where the fit fails, and a Kalman filter
with an acceleration state would be the next step.

## Problems we met and how we solved them

1. **The robot never moved in the first Gazebo check of the slalom (gate 1, task 3).** Every
   `/cmd_vel` was exactly zero and `/mpc_prediction` had no messages, so the node never got a
   goal. The bag had no `/new_position` at all. The goal had been published before the node was
   up, and `ros2 topic pub` messages are not stored, so a late subscriber never sees them. With the
   goal published 10 s after the node started, the same node drove to (1.78, 0.01). So it was the
   order of operations and not the code. Scenarios with a point goal now carry the goal in the
   `SCENARIOS` table, so no run depends on publish timing.
2. **RViz showed nothing of the robot.** The Lab 2 RViz config has no robot model and nothing
   that draws the body. We added a RobotModel display and a marker topic where the node draws the
   plank and the discs it believes in. A terminal on a different `ROS_DOMAIN_ID` also gives an
   empty RViz, and we now check the domain first.
3. **The Gazebo window changed the result.** With the window open the solve time roughly tripled
   and even Lab 2's own task read over 100 ms. All timed runs are headless. This also decided N.
4. **The three-disc plank grazed the obstacle** (see the safety margin above). Odometry error
   used up the margin, odometry drifted away from the truth after the contact, and the rest of the lap was wrong.
   Fixed with the 2 cm margin. The cost is the 0.28 m gap.
5. **A bug we inherited from Lab 2.** On Ctrl-C, Jazzy shut rclpy down before the `finally`
   block ran, the zero command failed with "publisher's context is invalid", and the robot kept
   its last command. We now start rclpy with the signal handler off, so Ctrl-C arrives as a normal
   interrupt, the node publishes the stop and then shuts down.
6. **Hard bounds on a measured state deadlock.** Known from Lab 2 task 4. Replaced by four soft
   constraints, shrunk by the plank's sweep radius.
7. **One table of numbers.** In Lab 2 the plot tool and the controller each held a copy of the
   obstacle numbers, and they drifted apart. Now the controller, the launch file, the analysis
   and the desk simulation all read the one `SCENARIOS` table.

8. **The with-future run passed by only 1 to 2 cm at the desk.** The controller that knows the obstacle's
   future passes about as close as the constraint allows, which Gazebo's odometry error (1.4 to 3.5 cm) could
   erase. We added 0.03 m of keep-out for moving obstacles (see scenario 3).
9. **Our first moving goal showed no benefit.** A slow ball moving away is caught by a faster
   robot whatever it believes. We changed the geometry so that the ball crosses the robot's path
   (see scenario 4).

## What changed against the proposal, and what did not work

- The first proposal was an articulated vehicle that bends in the middle, with three members.
  Version 2 replaced it with the plank on the Burger, with two members.
  `[PLACEHOLDER: one or two sentences on why, from Dominic.]`
- s1b obstacle moved from (0, 0.25) to (0, 0.36) with r = 0.08 m, because at (0, 0.25) the
  robot's start was inside the one-disc keep-out.
- The box is four numbers (x_min, x_max, y_min, y_max) and not one half-width, because the
  corridor is long in x and narrow in y.
- Circle runs are one lap. Lab 2 used two. One lap passes the obstacle once, which is all a pair needs.
- The 2 cm safety margin was not in the proposal. See the problems above.
- Scenarios 3 and 4 are built as proposed: the obstacle centre as a TVP fed its future, and a
  constant velocity fit for the goal, each against a baseline that only knows the position now.
  Two details were not in the proposal: the 0.03 m extra keep-out for the moving obstacle, and the
  2 cm of noise we add to the position of the goal so that the fit has something to average.

## Limitations

- It is simulation only. Wheel slip, the delay of a real robot and sensor noise are only what Gazebo
  models. The proposal said so, because the repeatable truth and obstacle timing are the point.
- The controller trusts odometry. The largest error over a run was 1.4 to 3.5 cm in scenarios 1 to 3
  and up to 8 cm in scenario 4, and about 1 m after a contact. The 2 cm margin covers the first and not the
  last.
- The discs are conservative. At the 0.28 m gap the real plank has 0.04 m to spare on each side, and
  the three discs plus the margin still reject it, so the controller stops 1.25 m short.
- The horizon reaches 0.44 m (N = 20). Going round an obstacle with a 0.5 m keep-out cannot be
  planned from far away, so scenarios 1 and 2 are built so that no detour is longer than the reach.
- One body, a plank along the heading, and circular obstacles only.
- Solve times depend on the machine and on the Gazebo window. Ours are headless, on two machines. The
  95th percentile stays under the 100 ms tick, but single ticks do not: in scenario 3 the slowest were
  116 ms with its future and 127 to 248 ms without, while the avoidance was being planned.
- Scenario 3 has one obstacle on a straight line at a constant speed that we know. Real obstacles
  change speed and direction, and need a tracker.
- Scenario 4's ball also moves in a straight line at a constant speed, so the estimator is exact for
  its motion. The noise is Gaussian and the same size at every tick.
- Three runs of each mode show the verdicts do not change, but three is a small sample for the
  size of the gain in scenario 4, which varies with the noise.
- We do not know why, after the contact in scenario 3, the robot's true heading kept turning while its
  odometry did not. We did not test whether the wheels slipped.

## What we learned

`[PLACEHOLDER: Dominic to rewrite in his own words. Draft from the work so far:]`

- A measurement has to be independent of the thing measured. Grading with ground truth against the
  exact rectangle caught a graze that the controller's own discs said was clear.
- A soft constraint with a large linear penalty did not deadlock where a hard bound on a measured state
  did in Lab 2, and it costs nothing when a plan that keeps clear exists.
- Simulation hides timing. The Gazebo window tripled the solve time, and a goal published before the
  node was up was never seen.
- A safety margin is a trade. The 2 cm bought robustness to odometry error and cost the 0.28 m gap.
- One table of numbers for the controller, the launch file and the analysis stops copies drifting.

## Reproduction on the desktop, 2026-10-21

The earlier runs were recorded on the laptop. On 2026-10-21 we built the workspace on the desktop
and repeated four of them headless, on their own ROS domain and Gazebo partition, to check that
the numbers hold on a second machine. Each run was graded from ground truth against the exact
rectangle with `analysis/plot_run.py`. The bags are in `bags/desk_check/` and are not committed.

| run | laptop, 15 to 17 Oct | desktop, 21 Oct |
|---|---|---|
| s2_030, three discs | pass, clearance 0.050 m, goal in 8.9 to 9.1 s | pass, clearance 0.0500 m, goal in 9.1 s |
| s2_030, one disc | stopped 1.1 to 1.3 m short, safe, clearance 0.061 m | stopped 1.314 m short, safe, clearance 0.0631 m |
| s1a, three discs | clearance 0.011 m, max path error 0.075 m | clearance 0.0141 m, max path error 0.0742 m |
| s1a, one disc | clearance 0.089 m, max path error 0.207 m | clearance 0.0915 m, max path error 0.2207 m |

The scenario 2 results are the same to within 2 mm and the verdicts are the same in all four
runs. The scenario 1 numbers differ by up to 1.4 cm, which is what we expect from a closed loop
in a physics simulator that is not bit-exact between machines. Odometry ended 1.3 to 2.5 cm from
the ground truth, as before.

We repeated the s1b and s2_050 runs on 2026-10-24 for the video. Again the verdicts and the clearances
agree: s2_050 gives +0.150 m for both footprints and the one disc stops 1.18 m short, exactly as on the
laptop. s1b gives a max path error of 0.270 m (one disc) against 0.029 m (three discs), against 0.302 m and
0.027 m on the laptop, and s1a gives 0.220 m against 0.081 m, against 0.207 m and 0.075 m.

Solve time differs between machines, so we report it per machine. On the desktop the median was
25.5 and 27.7 ms with one disc and 29.6 and 41.5 ms with three discs, and the 95th percentile
was 38 to 70 ms, inside the 100 ms tick. A few single ticks took 120 to 290 ms. The 41.5 ms median
was the first run after the build, so it may include a cold start.

We also downloaded the laptop bags from the shared Drive folder and regraded all 16 runs with
`analysis/plot_run.py`. Every clearance, every pass or stop verdict and every path error matches
the tables above, to the precision we wrote them down. The solve times recompute to a median of
the per-run medians of 21.9 ms with one disc and 32.9 ms with three, and a worst 95th percentile of
83.1 ms (s1b with one disc). So the tables are recomputed from saved bags and not copied from a log.

The four zero-margin runs reproduce the graze as well. Regraded from their bags, the s1a run with
three discs and no margin gives a real clearance of -0.0021 m (contact), a mean path error of
0.371 m and an odometry error of 1.035 m at the end. The same scenario with one disc stays clear at
+0.0786 m, and the two s2_050 runs behave as with the margin (one disc stopped 1.139 m short, three
discs pass with 0.150 m).

## Open items before the report can be written

1. The Canvas brief for the report (page limit, sections, code and video).
2. The demo video: replay clips are made by `analysis/replay_video.py` and joined by
   `analysis/make_demo_video.py`. Dominic decides which clips go in, and uploads the video.
4. Contributions agreed with Abdalrahman, his student ID and the video link.
5. The block diagram updated to what was built.
6. A pass over the code before submission, so each file starts with a short docstring and comments
   remain only where something is not obvious. `mpc_node.py` and the launch file still refer to
   decisions and log entries (for example "decision Q2", "LOG.md D9"), which belong in the log and
   not in the code.
7. The lecture links filled in from the slides.
