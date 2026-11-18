# Final recording runsheet: scenarios 3 and 4 in Gazebo and RViz

This is the runsheet for the four demo recordings of the resubmission. Follow it from top to bottom.
For these four runs it replaces section 2 of `project/RUNSHEET.md`.

## The four runs

| run | name (bag and video) | scenario | what differs | node parameters |
|---|---|---|---|---|
| 1 | `s3_future` | s3, the crossing cylinder | told the cylinder's future | `-p prediction:=future` |
| 2 | `s3_now` | s3 | only told its position now | `-p prediction:=now` |
| 3 | `s4_fit` | s4, the moving ball | constant velocity fit | `-p goal_estimate:=fit -p noise_seed:=1` |
| 4 | `s4_hold` | s4 | last seen position held | `-p goal_estimate:=hold -p noise_seed:=1` |

Every run uses the graded settings: the three-disc plank, horizon 20, all other parameters at their
defaults, noise seed 1 for scenario 4 (as in the graded `s4_fit_1` and `s4_hold_1`).

- Bags go to `~/R7021E-group6/project/bags/final_demo_bags/<name>`.
- Videos go to `~/R7021E-group6/project/videos/final_demo/<name>.mp4`.

## How these bags match the earlier ones

Every bag of the project was recorded the same way, and these are no different:

- the same four terminals in the same order: Gazebo (T1), the recorder (T4), then the node (T2);
- the same topic list as every bag recorded after the presentation: the graded list plus `/mpc_stats`;
- the node runs for 17 s and is then stopped with Ctrl-C, with up to 8 s to stop. This is exactly what
  `analysis/run_headless.py` did for the graded runs, written as one line for T2;
- the same grader, `analysis/plot_run.py`.

The one difference is on purpose: here the Gazebo window and RViz are open (`gui:=true rviz:=true`),
because the examiners want to see the Gazebo world. The windows slow the solver (LOG.md, decision D1).
So these four bags are demo bags. The numbers in the report stay those of the headless bags. We grade
each demo bag only to check that the clip shows the graded behaviour.

---

## 0. Once, before run 1

Open four terminals. Run these two lines in **every** terminal:

```bash
source ~/R7021E-group6/project/resubmission/env.sh
printenv ROS_DOMAIN_ID
```

All four must print the same value (or all print nothing).

In T1, check the disk. You need at least 1 GB available for the four videos:

```bash
df -h ~
```

If it shows less than 1G under "Avail", free space first (`~/.cache` holds about 685 MB) and check
again.

In T1, build once (the launch file has the new `rviz` argument):

```bash
cd ~/R7021E-group6/project/ros2_ws && colcon build --symlink-install
```

In T1, make the video folder and check that both folders are empty:

```bash
mkdir -p ~/R7021E-group6/project/videos/final_demo
ls -A ~/R7021E-group6/project/bags/final_demo_bags ~/R7021E-group6/project/videos/final_demo
```

The screen recorder is the desktop's own: press **Print**, choose the video camera icon, choose
**Screen**, press the round record button. A red timer appears in the top bar. Stop it with the red
button in the top bar. The video is saved in `~/Videos/Screencasts/`.

### The screen layout (the same in all four runs)

- Gazebo window: top left, half the screen width, about three quarters of the height.
- RViz window: top right, half the screen width, about three quarters of the height.
- Terminal T2: along the bottom quarter of the screen, full width. It shows the node's log, so the
  viewer can read `prediction: future` or `estimate: fit`.
- T1 and T4: behind the others.
- In Gazebo, use the mouse to zoom and tilt until you see, from above at a slight angle: the robot at
  (0, 0), the goal area at (2, 0), and the cylinder at (1.0, 1.2) (scenario 3) or the ball at
  (1.2, -1.2) and the space up to y = 2 (scenario 4).
- In RViz, keep the saved view and scroll to zoom until the same area is in view.

---

## Run 1: `s3_future`

1. T1, check that no Gazebo, node or recorder is left over from before. It must print nothing:

   ```bash
   pgrep -af "gz sim|mpc_node|ros2 bag"
   ```

   If it prints anything, stop it all, wait 5 s, and check again until it prints nothing:

   ```bash
   pkill -INT -f "ros2 bag record"; pkill -f mpc_node; pkill -f "gz sim"
   ```

2. T1, start Gazebo and RViz:

   ```bash
   ros2 launch r7021e_project project_sim.launch.py scenario:=s3 gui:=true rviz:=true
   ```

3. Wait until both windows are open and T1 has stopped printing (at least 15 s). Arrange the windows
   and the views as in "The screen layout".

4. T4, start the recorder:

   ```bash
   ros2 bag record -o ~/R7021E-group6/project/bags/final_demo_bags/s3_future /odom /ground_truth /cmd_vel /mpc_prediction /mpc_solve_time /mpc_footprint /mpc_obstacles /mpc_ghosts /mover_1/pose /target/pose /tf /tf_static /mpc_stats
   ```

   Wait 3 s, until it has printed its "Subscribed to topic" lines.

5. Paste this line into T2, but **do not press Enter yet**:

   ```bash
   ros2 run r7021e_project mpc_node --ros-args -p scenario:=s3 -p footprint:=three -p prediction:=future -p use_sim_time:=true & NODE=$!; sleep 17; kill -INT -- -$NODE; echo ">>> 17 s: node told to stop. Stop the screen recording now."; sleep 8; kill -KILL -- -$NODE 2>/dev/null && echo ">>> the node did not stop and was killed"; wait
   ```

6. Start the screen recording (Print, video, Screen, record). Then click into T2 and press Enter.

7. Watch. The cylinder starts moving with the robot. The plank turns clockwise on the spot while the
   cylinder passes, then the robot drives on to the goal and stops (about 11.5 s).

8. When T2 prints `>>> 17 s: node told to stop`, stop the screen recording (red button in the top bar).

9. Wait until T2 shows its prompt again (about 8 s; you see `Done`).

10. T4: press Ctrl-C **once** and wait for `Recording stopped`.

11. T1: press Ctrl-C and wait for the prompt. Both windows close.

12. T1, save the video under its name:

    ```bash
    mv -n "$(ls -t ~/Videos/Screencasts/*.mp4 | head -1)" ~/R7021E-group6/project/videos/final_demo/s3_future.mp4
    ```

13. T1, check the bag and grade it. The result line is also written to the takes log:

    ```bash
    ls ~/R7021E-group6/project/bags/final_demo_bags/s3_future
    cd ~/R7021E-group6/project/analysis && python3 plot_run.py ../bags/final_demo_bags/s3_future --scenario s3 --footprint three --line | tee -a ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

    `ls` must show `metadata.yaml` and one `.mcap`. **Keep** the take if the line ends in `PASS`
    (graded runs: about +0.04 to +0.07 m, goal about 11.4 to 11.8 s). Otherwise follow "If a take does
    not match" at the end.

    ```bash
    echo "s3_future take 1: kept" >> ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

## Run 2: `s3_now`

1. T1, check that no Gazebo, node or recorder is left over from before. It must print nothing:

   ```bash
   pgrep -af "gz sim|mpc_node|ros2 bag"
   ```

   If it prints anything, stop it all, wait 5 s, and check again until it prints nothing:

   ```bash
   pkill -INT -f "ros2 bag record"; pkill -f mpc_node; pkill -f "gz sim"
   ```

2. T1:

   ```bash
   ros2 launch r7021e_project project_sim.launch.py scenario:=s3 gui:=true rviz:=true
   ```

3. Wait until both windows are open and T1 is quiet (at least 15 s). Arrange as in "The screen layout".

4. T4:

   ```bash
   ros2 bag record -o ~/R7021E-group6/project/bags/final_demo_bags/s3_now /odom /ground_truth /cmd_vel /mpc_prediction /mpc_solve_time /mpc_footprint /mpc_obstacles /mpc_ghosts /mover_1/pose /target/pose /tf /tf_static /mpc_stats
   ```

   Wait 3 s.

5. Paste into T2, do not press Enter yet:

   ```bash
   ros2 run r7021e_project mpc_node --ros-args -p scenario:=s3 -p footprint:=three -p prediction:=now -p use_sim_time:=true & NODE=$!; sleep 17; kill -INT -- -$NODE; echo ">>> 17 s: node told to stop. Stop the screen recording now."; sleep 8; kill -KILL -- -$NODE 2>/dev/null && echo ">>> the node did not stop and was killed"; wait
   ```

6. Start the screen recording, then click into T2 and press Enter.

7. Watch. The robot drives straight on, the plank touches the cylinder at about 3.5 s, and after that
   the robot spins and stops far from the goal. RViz and Gazebo then show the plank in different places,
   because odometry is about 1 m off after the contact.

8. When T2 prints `>>> 17 s`, stop the screen recording.

9. Wait for the T2 prompt.

10. T4: Ctrl-C **once**, wait for `Recording stopped`.

11. T1: Ctrl-C, wait for the prompt.

12. T1:

    ```bash
    mv -n "$(ls -t ~/Videos/Screencasts/*.mp4 | head -1)" ~/R7021E-group6/project/videos/final_demo/s3_now.mp4
    ```

13. T1:

    ```bash
    ls ~/R7021E-group6/project/bags/final_demo_bags/s3_now
    cd ~/R7021E-group6/project/analysis && python3 plot_run.py ../bags/final_demo_bags/s3_now --scenario s3 --footprint three --line | tee -a ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

    **Keep** the take if `min clearance` is below 0 (contact) and the line ends in `FAIL` (graded runs:
    -0.006 to -0.008 m, ending 1.0 to 1.6 m short).

    ```bash
    echo "s3_now take 1: kept" >> ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

## Run 3: `s4_fit`

1. T1, check that no Gazebo, node or recorder is left over from before. It must print nothing:

   ```bash
   pgrep -af "gz sim|mpc_node|ros2 bag"
   ```

   If it prints anything, stop it all, wait 5 s, and check again until it prints nothing:

   ```bash
   pkill -INT -f "ros2 bag record"; pkill -f mpc_node; pkill -f "gz sim"
   ```

2. T1:

   ```bash
   ros2 launch r7021e_project project_sim.launch.py scenario:=s4 gui:=true rviz:=true
   ```

3. Wait until both windows are open and T1 is quiet (at least 15 s). Arrange as in "The screen layout".

4. T4:

   ```bash
   ros2 bag record -o ~/R7021E-group6/project/bags/final_demo_bags/s4_fit /odom /ground_truth /cmd_vel /mpc_prediction /mpc_solve_time /mpc_footprint /mpc_obstacles /mpc_ghosts /mover_1/pose /target/pose /tf /tf_static /mpc_stats
   ```

   Wait 3 s.

5. Paste into T2, do not press Enter yet:

   ```bash
   ros2 run r7021e_project mpc_node --ros-args -p scenario:=s4 -p footprint:=three -p goal_estimate:=fit -p noise_seed:=1 -p use_sim_time:=true & NODE=$!; sleep 17; kill -INT -- -$NODE; echo ">>> 17 s: node told to stop. Stop the screen recording now."; sleep 8; kill -KILL -- -$NODE 2>/dev/null && echo ">>> the node did not stop and was killed"; wait
   ```

6. Start the screen recording, then click into T2 and press Enter.

7. Watch. The green ball moves up and to the right. The robot heads for where the ball is going (the
   green ghosts in RViz), lines up with its path by about 8 s, and follows close behind it.

8. When T2 prints `>>> 17 s`, stop the screen recording.

9. Wait for the T2 prompt.

10. T4: Ctrl-C **once**, wait for `Recording stopped`.

11. T1: Ctrl-C, wait for the prompt.

12. T1:

    ```bash
    mv -n "$(ls -t ~/Videos/Screencasts/*.mp4 | head -1)" ~/R7021E-group6/project/videos/final_demo/s4_fit.mp4
    ```

13. T1:

    ```bash
    ls ~/R7021E-group6/project/bags/final_demo_bags/s4_fit
    cd ~/R7021E-group6/project/analysis && python3 plot_run.py ../bags/final_demo_bags/s4_fit --scenario s4 --footprint three --line | tee -a ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

    **Keep** the take if the line shows `within 0.2 m at` a time, not `never` (graded seed 1: 8.9 s,
    mean 0.138 m; all graded fit runs: mean 0.14 to 0.21 m). If T2 printed `the node did not stop`,
    grade it over the normal window instead (see "Notes").

    ```bash
    echo "s4_fit take 1: kept" >> ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

## Run 4: `s4_hold`

1. T1, check that no Gazebo, node or recorder is left over from before. It must print nothing:

   ```bash
   pgrep -af "gz sim|mpc_node|ros2 bag"
   ```

   If it prints anything, stop it all, wait 5 s, and check again until it prints nothing:

   ```bash
   pkill -INT -f "ros2 bag record"; pkill -f mpc_node; pkill -f "gz sim"
   ```

2. T1:

   ```bash
   ros2 launch r7021e_project project_sim.launch.py scenario:=s4 gui:=true rviz:=true
   ```

3. Wait until both windows are open and T1 is quiet (at least 15 s). Arrange as in "The screen layout".

4. T4:

   ```bash
   ros2 bag record -o ~/R7021E-group6/project/bags/final_demo_bags/s4_hold /odom /ground_truth /cmd_vel /mpc_prediction /mpc_solve_time /mpc_footprint /mpc_obstacles /mpc_ghosts /mover_1/pose /target/pose /tf /tf_static /mpc_stats
   ```

   Wait 3 s.

5. Paste into T2, do not press Enter yet:

   ```bash
   ros2 run r7021e_project mpc_node --ros-args -p scenario:=s4 -p footprint:=three -p goal_estimate:=hold -p noise_seed:=1 -p use_sim_time:=true & NODE=$!; sleep 17; kill -INT -- -$NODE; echo ">>> 17 s: node told to stop. Stop the screen recording now."; sleep 8; kill -KILL -- -$NODE 2>/dev/null && echo ">>> the node did not stop and was killed"; wait
   ```

6. Start the screen recording, then click into T2 and press Enter.

7. Watch. Same ball, same noise. The robot aims at the last position it saw (all green ghosts on one
   spot), falls behind and never gets within 0.2 m.

8. When T2 prints `>>> 17 s`, stop the screen recording.

9. Wait for the T2 prompt.

10. T4: Ctrl-C **once**, wait for `Recording stopped`.

11. T1: Ctrl-C, wait for the prompt.

12. T1:

    ```bash
    mv -n "$(ls -t ~/Videos/Screencasts/*.mp4 | head -1)" ~/R7021E-group6/project/videos/final_demo/s4_hold.mp4
    ```

13. T1:

    ```bash
    ls ~/R7021E-group6/project/bags/final_demo_bags/s4_hold
    cd ~/R7021E-group6/project/analysis && python3 plot_run.py ../bags/final_demo_bags/s4_hold --scenario s4 --footprint three --line | tee -a ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

    **Keep** the take if the line shows `within 0.2 m at never` (graded seed 1: mean 0.341 m; all
    graded hold runs: 0.30 to 0.34 m).

    ```bash
    echo "s4_hold take 1: kept" >> ~/R7021E-group6/project/resubmission/final-demo-takes.txt
    ```

---

## If a take does not match

The windows slow the solver, so a close run can come out differently. A take that does not match is
not deleted: it is moved aside under a take number, and the run is recorded again under the same
name. Example for `s3_future`, take 1 (use the run's own name and the take number):

```bash
mkdir -p ~/R7021E-group6/project/bags/final_demo_bags/discarded ~/R7021E-group6/project/videos/final_demo/discarded
mv -n ~/R7021E-group6/project/bags/final_demo_bags/s3_future ~/R7021E-group6/project/bags/final_demo_bags/discarded/s3_future_take1
mv -n ~/R7021E-group6/project/videos/final_demo/s3_future.mp4 ~/R7021E-group6/project/videos/final_demo/discarded/s3_future_take1.mp4
echo "s3_future take 1: discarded" >> ~/R7021E-group6/project/resubmission/final-demo-takes.txt
```

Then do the whole run again from step 1, and log the new take as `take 2`. At most three takes per run.
If take 3 also does not match, keep take 3, log it as `take 3: kept, does not match`, and say so in
the report.

## Notes

- **Never press Ctrl-C in T2 while the timed line runs.** Ctrl-C stops only the `sleep`, and the node
  keeps running in the background. It then drives the robot in the next launch as soon as Gazebo
  starts. If you must abort a take, run `pkill -f mpc_node` in T1, discard the take, and start again
  from step 1.
- **Stopping a take early.** If you stop anything by hand before T2 prints `>>> 17 s`, that
  take is not like the others: discard it as above and record again.
- **The node did not stop** (T2 prints `>>> the node did not stop and was killed`). A Ctrl-C that
  arrives during a solve is swallowed by the node; this is known (report section 7.3). The video is
  still fine, because you stopped it at `>>> 17 s`. For scenario 4, grade the bag over the normal
  window instead:

  ```bash
  cd ~/R7021E-group6/project/resubmission/analysis && python3 grade_extra.py ../../bags/final_demo_bags/s4_fit --scenario s4 --window 15.5 | tee -a ~/R7021E-group6/project/resubmission/final-demo-takes.txt
  ```

- **Nothing moves** (T2 prints `waiting for the poses of the moving obstacle or goal`): T1 and T2 have
  different scenario names, or a different `ROS_DOMAIN_ID`. Stop everything, discard the take, and
  start again from step 1.
- **The recorder ends without `metadata.yaml`**: it was killed, not stopped. Discard the take and
  record again.
- **No video in `~/Videos/Screencasts/`**: run `ls -t ~/Videos ~/Videos/*` to find the newest `.mp4`,
  and use that path in the `mv` line.

## After run 4

Check that all four bags and all four videos are there:

```bash
ls ~/R7021E-group6/project/bags/final_demo_bags ~/R7021E-group6/project/videos/final_demo
cat ~/R7021E-group6/project/resubmission/final-demo-takes.txt
```

Put them in the upload folder as hard links (no extra disk space):

```bash
mkdir -p ~/R7021E-resubmission-to-upload/bags/final_demo_bags
cp -al ~/R7021E-group6/project/bags/final_demo_bags/s3_future ~/R7021E-group6/project/bags/final_demo_bags/s3_now ~/R7021E-group6/project/bags/final_demo_bags/s4_fit ~/R7021E-group6/project/bags/final_demo_bags/s4_hold ~/R7021E-resubmission-to-upload/bags/final_demo_bags/
ln ~/R7021E-group6/project/videos/final_demo/s3_future.mp4 ~/R7021E-group6/project/videos/final_demo/s3_now.mp4 ~/R7021E-group6/project/videos/final_demo/s4_fit.mp4 ~/R7021E-group6/project/videos/final_demo/s4_hold.mp4 ~/R7021E-resubmission-to-upload/videos/
```

Then add the four bags to the bags index. Upload
`~/R7021E-resubmission-to-upload/` to the Drive and put the two links into the report.

## What to say over each clip (optional)

1. `s3_future`: "The controller is told where the cylinder will be. The red ghosts in RViz are its
   predicted positions. The plank turns clockwise on the spot while the cylinder passes, then drives on
   to the goal. In section 7.1 we show that turning the other way is faster."
2. `s3_now`: "Same scenario, but the controller only knows where the cylinder is now, so all the ghosts
   sit on one spot. It reacts too late and the plank touches the cylinder. After the contact RViz and
   Gazebo disagree, because odometry is off by about a metre. Gazebo shows the truth."
3. `s4_fit`: "The green ball moves at constant speed. The controller sees it with 2 cm of noise and fits a
   straight line. The green ghosts are where it expects the ball. The robot follows close behind it."
4. `s4_hold`: "Same ball and same noise, but the controller aims at the last position it saw. It falls
   behind the ball and never gets within 20 cm."
