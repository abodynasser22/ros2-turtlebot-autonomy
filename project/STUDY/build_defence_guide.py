#!/usr/bin/env python3
"""Build "Project Defence Guide.html": the retrieval guide for the project presentation.

    python3 build_defence_guide.py     # needs defence_template.html, writes the guide next to this file

The page is one file with no outside links. It keeps what you type (map links, predictions, ratings) in this
browser's local storage. Every number in it comes from ../OBSERVED.md or the report. Statements that are
derived from the constraint and not measured say so on the page.
"""

import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PLOTS = os.path.join(HERE, '..', 'plots')

IMAGES = {
    'dyn_s2': 'dynamics_s2.png',
    'sweep': 's2_sweep.png',
    'dyn_s1a': 'dynamics_s1a.png',
    's1a_pair': 's1a_pair.png',
    'dyn_s3': 'dynamics_s3.png',
    's3_pair': 's3_pair.png',
    'dyn_s4': 'dynamics_s4.png',
    's4_pair': 's4_pair.png',
}

# ------------------------------------------------------------------ the blind map

KEYWORDS = [
    'unicycle model', 'non-holonomic', 'MPC horizon N = 20', 'TVP', 'soft constraint', 'slack penalty 10^4',
    'keep-out ring', 'three discs', 'margin 0.02 m', 'mover margin 0.03 m', 'delay compensation', 'odometry',
    'ground truth', 'rectangle clearance', 'future vs now', 'ghost circles', 'least squares fit', 'noise 2 cm',
    'hold', 'solve time 100 ms', 'the 0.28 m gap', 'contact', 'headless', 'Lab 2', 'Lecture 4',
]

GAP_QUESTIONS = [
    'Which two keywords explain why the one-disc robot stopped at x = 0.687 m? Link them and say why.',
    'What connects "odometry", "contact" and one of the labs?',
    'Where do "delay compensation" and "future vs now" meet? Look at the formula o(k) = o_now + v (d + k) dt.',
    'Which keyword has no link yet? Either link it or ask why it is on the map.',
    'Which of your links would break if the robot could move sideways?',
]

# Claims to attack. Each one is plausible and partly wrong. "breaks" is shown after you have written your own.
CLAIMS = [
    ('Three discs let the robot use any gap that the plank fits through.',
     'The discs cover the plank with room to spare, and the margin adds 0.02 m. The plank is 0.20 m wide, so it fits a '
     '0.28 m gap with 0.04 m on each side, and the three-disc robot still stopped (1.25 m short). It needs 0.30 m.'),
    ('A soft constraint with a penalty of 10^4 behaves like a hard one.',
     'It behaves like one when a clear plan exists, because the slack is then zero. It is not a guarantee: it allows a '
     'small violation when that is cheap, and it is the reason the solver never becomes infeasible. The three-disc '
     'keep-out at the 0.30 m gap is about 0.3 mm short (derived, see card 2), and the robot passed.'),
    ('If the controller knows the obstacle\'s future, the robot passes safely.',
     'It passed three times out of three, with +0.048 to +0.056 m, for one obstacle on a straight line at constant '
     'speed with a path that we chose. That is evidence for this setup, not a proof. The extra 0.03 m of mover margin '
     'was needed because at the desk the clearance was only 1 to 2 cm.'),
    ('The fit beats the hold because it knows where the ball will be.',
     'It is closer (0.183 m against 0.323 m over the last 5 s), but the path is the same. The gain is a smaller lag '
     'behind the ball, 0.19 to 0.26 m against 0.36 to 0.40 m at 8 s. The robot is only 7 percent faster than the ball, '
     'so neither catches it.'),
    ('Grading against the ground truth is the independent check.',
     'It is independent of the controller. It is not independent of the simulation: the exact rectangle is our model of '
     'the plank, and a real robot has no ground truth. We do not claim it for hardware.'),
    ('Odometry was good enough, so the controller could trust it.',
     'It was within 1.4 to 3.5 cm of the truth in scenarios 1 to 3, up to 8 cm in scenario 4. After the contact in '
     'scenario 3 without the future it was about 1 m off, and the controller steered from a pose that was wrong.'),
]

# ------------------------------------------------------------------ predict, then check

CARDS = [
    dict(
        id='c1', title='1. One disc at the 0.30 m gap',
        setup='Scenario 2. Two posts of r = 0.10 m at x = 1.0 m, gap 0.30 m, goal (2.0, 0.0). One disc: keep-out '
              '0.10 + 0.269 + 0.02 = 0.389 m around each post centre.',
        predict='Where does the robot end up, how long does it take to get there, and how close is the real plank to '
                'the posts? Write numbers, even if you are guessing.',
        events=[[0, 'first command'], [3.48, 'stops, x = 0.687 m'], [6, 'still there']], tmax=8,
        observed=[
            'Stops at x = 0.687 m, 3.48 s after the first command, and stays there: 1.31 m short of the goal.',
            'Real clearance to each post +0.061 m. No contact.',
            'The two keep-out rings meet the centre line at x = 0.702 m, so it stopped within 1.5 cm of where the '
            'geometry says it must.',
        ],
        derived='Ring radius R = 0.10 + 0.269 + 0.02 = 0.389 m. The post centres are 0.25 m from the centre line. The '
                'ring reaches the centre line at a distance sqrt(0.389^2 - 0.25^2) = 0.298 m before the post, so '
                'x = 1.0 - 0.298 = 0.702 m. This is a calculation from the constraint, checked against the bag.',
        figure='dyn_s2', caption='Scenario 2, 0.30 m gap: robot x and commanded speed, one disc against three discs.',
        notest='We did not look at the size of the slack at the stop.'),
    dict(
        id='c2', title='2. Three discs at the 0.30 m gap',
        setup='Same corridor, three discs of r = 0.130 m at -0.167, 0 and +0.167 m. Keep-out 0.10 + 0.130 + 0.02 = '
              '0.25 m from each post centre, and the post centres are 0.25 m from the centre line.',
        predict='Does it pass? Does it slow down, and where? What real clearance do you expect on each side?',
        events=[[0, 'first command'], [3.8, 'speed dips'], [4.55, 'min 0.12 m/s'], [5.3, 'last dip'], [9.08, 'reaches goal']],
        tmax=10,
        observed=[
            'Passes. Reaches (2.0, 0.0) in 9.08 s.',
            'Commanded speed is 0.22 m/s except for short dips between 3.8 and 5.3 s, down to 0.12 m/s, while it is '
            'between the posts.',
            'Real clearance +0.050 m to each post, which is (0.30 - 0.20) / 2.',
            'Median solve time 33 ms (22 ms with one disc).',
        ],
        derived='The exact radius is r3 = sqrt((0.50/6)^2 + 0.10^2) = 0.1302 m, so the keep-out needs a distance of '
                '0.10 + 0.1302 + 0.02 = 0.2502 m and the posts are 0.25 m from the line. That is 0.2 mm short per '
                'side, 0.3 mm in the gap. Our reading, not tested: the soft constraint lets the robot pass with a '
                'violation that small, and the dips in speed are the solver trading it against the goal.',
        figure='dyn_s2', caption='The same figure: the blue line is the three-disc robot.',
        notest='We did not record the slack, so the reading about the dips is a reading.'),
    dict(
        id='c3', title='3. Three discs at the 0.28 m gap',
        setup='Same corridor with the posts 0.02 m closer. The plank is 0.20 m wide.',
        predict='The real plank has 0.04 m to spare on each side. Does the robot go through?',
        events=None, tmax=0,
        observed=[
            'It also stops: 1.25 m short of the goal, real clearance +0.037 m.',
            'Its keep-out with the margin needs a gap of about 0.30 m, although the real plank has 0.04 m on each side.',
        ],
        derived='Shortfall: 0.3003 - 0.28 = 0.020 m, against 0.0003 m at the 0.30 m gap. That is about 70 times more '
                'violation to pay for with slack at 10^4 per unit. Derived, not measured.',
        figure='sweep', caption='Real clearance against the gap in scenario 2, filled for a pass.',
        notest='The time it stopped was not read off for this run. Do not quote one.'),
    dict(
        id='c4', title='4. Scenario 1: the circle, one disc against three',
        setup='A lap of a circle of r = 0.8 m, with an obstacle of r = 0.12 m at (0, 0.62). The goal moves along the '
              'circle. Both footprints complete the lap.',
        predict='Which footprint leaves the circle more to get round the obstacle, and which one passes closer to it?',
        events=[[0, 'first command'], [17.4, 'closest, one disc'], [18.5, 'closest, three discs']], tmax=30,
        observed=[
            'One disc leaves the circle by at most 0.207 m, three discs by 0.075 m.',
            'Real clearance +0.089 m (one disc) against +0.011 m (three discs): the price of staying on the path.',
            'Figure of eight (obstacle at (0, 0.36), r = 0.08 m): 0.302 m against 0.027 m, and clearance +0.025 m '
            'against +0.043 m.',
        ],
        derived='If the constraint holds, the discs cover the plank, so the real clearance is at least the margin '
                '(0.02 m). The +0.025 m of the one-disc robot on the eight is inside that. Derived, not measured.',
        figure='dyn_s1a', caption='Scenario 1, circle: distance from the circle and real clearance, one disc against three.',
        notest='We did not look into why the one-disc run has less clearance than the three-disc run on the eight.'),
    dict(
        id='c5', title='5. Scenario 3 with its future',
        setup='A cylinder of r = 0.10 m starts at (1.0, 1.2) and moves at 0.30 m/s towards -y. It crosses the robot\'s '
              'line (y = 0) at 3.99 s. The controller is given o(k) = o_now + v (d + k) dt for every horizon step.',
        predict='What does the robot do, and when? Does it wait, swerve, or something else? Where is it when the '
                'obstacle crosses, and what is the smallest real clearance?',
        events=[[0, 'first command'], [1.8, 'first reaction'], [3.42, 'stopped, x = 0.70 m'], [3.98, 'obstacle crosses'],
                [4.7, 'heading -90 deg'], [5.2, 'smallest clearance'], [5.9, 'back above -45 deg'], [11.45, 'goal']],
        tmax=12,
        observed=[
            'Straight at 0.22 m/s until the first reaction at 1.80 to 1.83 s (obstacle at y = 0.64, robot at x = 0.36): '
            'about 2.2 s before the crossing, close to the 2.0 s horizon.',
            'Turns clockwise while still driving, then brakes: below 0.05 m/s at 3.42 to 3.44 s, at x = 0.70 to 0.71 m.',
            'Keeps turning in place. Heading -35 degrees at 3.4 s, -61 degrees at the crossing (3.98 s), -90 degrees at '
            '4.7 s, back above -45 degrees at 5.9 to 6.0 s.',
            'Real clearance 0.083 to 0.088 m at the crossing. Smallest +0.049, +0.048, +0.056 m at 5.17 to 5.20 s.',
            'Speed above 0.2 m/s again at 5.3 s (4.5 s in one run). Goal in 11.4 to 11.5 s, 8.9 s for the open corridor.',
            'Odometry within 0.5 degrees of the true heading, position error 1.9 to 3.5 cm.',
        ],
        derived='Time to cross: 1.2 m / 0.30 m/s = 4.0 s (observed 3.99 s). Gap between surfaces at the minimum: the '
                'keep-out is 0.28 m = 0.10 + 0.03 + 0.130 + 0.02, so the surfaces are 0.28 - 0.10 - 0.130 = 0.05 m '
                'apart, and the measured +0.048 to +0.056 m is that number. -90 degrees puts the plank along the '
                'obstacle\'s direction of travel.',
        figure='dyn_s3', caption='Scenario 3, run 1 of each: speed, real clearance, positions and solve time. Blue: with its future.',
        notest='Why it turns and does not just wait. Our reading is that a plank lying along the path reaches less far '
               'across it. We did not test that. Do not say the turn is complete at the crossing: it is -61 degrees then.'),
    dict(
        id='c6', title='6. Scenario 3 with only its position now',
        setup='The same obstacle, but the controller is given o(k) = o_now for every step, so the obstacle looks still.',
        predict='When does the robot first react, and does it touch? If it does, by how much, and what happens '
                'afterwards? Think about what the robot believes about where it is.',
        events=[[0, 'first command'], [3.17, 'first reaction'], [3.34, 'speed < 0.05'], [3.5, 'contact'], [3.76, 'deepest, -7 mm'],
                [3.99, 'obstacle crosses'], [5.5, 'true heading still turning'], [7, 'heading differs by 213 deg']], tmax=9,
        observed=[
            'Straight at 0.22 m/s until 3.16 to 3.19 s (obstacle at y = 0.23 to 0.24, robot at x = 0.66). Speed below '
            '0.05 m/s at 3.31 to 3.38 s, at x = 0.69 m.',
            'First contact at 3.47, 3.53 and 3.54 s. Smallest clearance -0.008, -0.007, -0.006 m at 3.74 to 3.78 s. '
            'Below zero for 0.71, 0.51 and 0.48 s.',
            'The body is disturbed: roll up to 2.3 degrees, pitch up to 5.6 degrees, a rise of about 4 mm.',
            'The true heading keeps turning clockwise, 304 to 547 degrees in total, also while the commanded turn rate '
            'is the other way (run 1, from 5.5 s).',
            'Run 1: heading difference between truth and odometry 28 degrees at 5 s, 113 at 6 s, 213 at 7 s. The robot '
            'drives away from the goal (x from 0.73 m at 5.5 s to 0.38 m at 8 s).',
            'The three runs stop 1.04, 0.99 and 1.59 m short of the goal. Odometry ends 1.01, 0.96 and 1.57 m from the truth.',
        ],
        derived='At the first reaction the front disc is at x + 0.167 = 0.827 m and the obstacle at (1.0, 0.235), a '
                'distance of 0.29 m. The keep-out is 0.28 m. So the robot reacts when the obstacle\'s current position '
                'reaches the keep-out, and by then the obstacle is coming at it at 0.30 m/s while the stopped plank\'s '
                'front end (x = 0.69 + 0.25 = 0.94 m) is already inside the obstacle\'s lane (x from 0.90 to 1.10 m). '
                'Derived reading, not tested.',
        figure='dyn_s3', caption='The red lines of the same figure: the robot stops at 3.2 s, touches, and later moves away from the goal.',
        notest='WHY THE TRUE HEADING KEPT TURNING AFTER THE CONTACT, and whether the wheels slipped. We did not '
               'investigate. Never say "the wheels slipped" as a fact.'),
    dict(
        id='c7', title='7. Scenario 4: hold against fit',
        setup='A ball starts at (1.2, -1.2) and moves at (0.05, 0.20) m/s, 0.206 m/s. The robot\'s limit is 0.22 m/s. '
              'The controller sees the ball with 2 cm of noise. Hold: the goal is the last seen position. Fit: a '
              'least squares line through the last 10 samples (1.0 s), extended over the horizon.',
        predict='Both robots are at the speed limit. Which ends closer to the ball, by how much, and is the path '
                'different or only the lag?',
        events=[[0, 'first command'], [8, 'lined up with the ball\'s path'], [8.9, 'fit within 0.2 m (seed 1)'],
                [15, 'end of the lag figures']], tmax=16,
        observed=[
            'Both robots drive at 0.22 m/s for 99 percent of the run and both reach the turn-rate limit 0.8 rad/s.',
            'By 8 s both are lined up with the ball\'s path (sideways offset 0.08 to 0.11 m) and trail behind it.',
            'Behind the ball along its path at 8 s: fit 0.19, 0.26, 0.25 m; hold 0.40, 0.39, 0.36 m. At 15 s: fit '
            '0.10, 0.18, 0.17 m; hold 0.31, 0.30, 0.27 m. Both close the gap by about 0.01 m/s.',
            'First within 0.2 m: fit at 8.9, 13.9, 12.9 s; hold never. Mean distance over the last 5 s: fit 0.138, '
            '0.210, 0.200 m (mean 0.183 m), hold 0.341, 0.326, 0.301 m (mean 0.323 m).',
            'Odometry position error 2.1 to 4.6 cm (hold) and 4.8 to 8.0 cm (fit).',
        ],
        derived='43 percent: (0.323 - 0.183) / 0.323 = 0.43. Closing speed: the robot is 0.22 - 0.206 = 0.014 m/s '
                'faster than the ball, which is the 0.01 m/s that both robots close the gap by.',
        figure='dyn_s4', caption='Scenario 4, noise seed 1: distance to the ball, commanded speed and turn rate. Blue: fit.',
        notest='Do not say the fit "cuts across". The difference is how far behind the ball the robot ends up.'),
    dict(
        id='c8', title='8. The first moving goal that proved nothing',
        setup='Our first ball moved slowly away from the robot at 0.12 m/s. The desk simulation compared the fit '
              'with the hold.',
        predict='What do you expect the two modes to give, and why? Which property of the situation decides it?',
        events=[[0, 'ball moves away at 0.12 m/s']], tmax=4,
        observed=[
            'Mean distance 0.27 m against 0.29 m at the desk: almost no difference.',
            'We changed the geometry to the crossing one (the ball at (1.2, -1.2), moving (0.05, 0.20) m/s), where '
            'the desk gave 0.142 m against 0.313 m.',
        ],
        derived='The robot is faster than the ball (0.22 against 0.12 m/s) and the ball is ahead, so it catches up '
                'whatever it believes. A comparison needs a situation that can tell the options apart.',
        figure=None, caption='', notest='Gazebo was not run for the first ball. The numbers are from the desk simulation.'),
    dict(
        id='c9', title='9. Time: the solve time and the window',
        setup='Each control tick is 0.1 s, so the solve has to be faster than that.',
        predict='Which of N = 20, 40, 60 can run in a 0.1 s tick, and what does opening the Gazebo window do? When '
                'during scenario 3 is the solve slowest?',
        events=[[0, 'first command'], [3, 'avoidance planned'], [6, 'avoidance ends']], tmax=8,
        observed=[
            '95th percentile of the solve time, hardest case (0.30 m gap, three discs, desk simulation, window closed): '
            '59 ms at N = 20, 174 ms at N = 40, 367 ms at N = 60.',
            'The Gazebo window roughly triples the solve time, so every timed run is headless.',
            'Scenario 3, median between 3 and 6 s: 53 to 54 ms with its future (about 40 ms before and 30 ms after), '
            '60 to 72 ms without (about 29 ms before and after).',
            'Slowest single ticks: 72 to 116 ms with its future (one run above 100 ms), 127 to 248 ms without.',
            'Scenarios 1 and 2: median 22 ms (one disc), 33 ms (three discs), worst 95th percentile 83 ms.',
        ],
        derived='Reach at N = 20: 20 x 0.1 s x 0.22 m/s = 0.44 m.',
        figure=None, caption='',
        notest='What a single tick above 100 ms does to the behaviour. We did not investigate. Do not say that it caused the contact.'),
    dict(
        id='c10', title='10. The graze with no margin',
        setup='Our first runs of scenario 1 used no margin on the keep-out.',
        predict='The discs said clear. What did the real plank do, and what did odometry say about where the robot '
                'was?',
        events=[[0, 'first command'], [18.6, 'graze, -2.1 mm'], [25, 'odometry 0.22 m off']], tmax=30,
        observed=[
            'Three discs, circle, no margin: real clearance -2.1 mm (contact), 18.6 s after the first command, while '
            'odometry was 2.7 cm off the truth. The desk simulation had predicted +3.7 mm.',
            'Afterwards odometry drifted away from the truth, 0.22 m at 25 s and 1.03 m at the end of the lap, and the '
            'robot followed its circle in the wrong place. The cause of that drift was not tested.',
            'We added 0.02 m to every keep-out, the idea of Lab 3\'s inflation radius (0.120 m for a 0.105 m robot). It '
            'costs 4 cm of gap.',
        ],
        derived='Three discs now need 2 x (0.130 + 0.02) = 0.30 m, and one disc 0.579 m.',
        figure=None, caption='', notest='Why odometry drifted after the graze, and whether it is related. Not tested.'),
]

# ------------------------------------------------------------------ the numbers

NUMBERS = [
    ['Body and discs', [
        ['Plank', '0.50 x 0.20 m'],
        ['Disc radius, n = 1 / 2 / 3', '0.269 / 0.160 / 0.130 m'],
        ['Gap needed without margin, n = 1 / 2 / 3', '0.538 / 0.320 / 0.260 m'],
        ['Gap needed with the 0.02 m margin, one disc / three discs', '0.579 m / 0.30 m'],
        ['Disc centres, three discs', '-0.167, 0, +0.167 m from the axle'],
        ['Radius the plank sweeps turning on the spot', '0.269 m (the box is shrunk by it)'],
        ['Safety margin / mover margin', '0.02 m / 0.03 m (moving keep-out 0.28 m)'],
    ]],
    ['Controller', [
        ['Tick and horizon', '0.1 s, N = 20 (2.0 s)'],
        ['Reach at N = 20', '0.44 m'],
        ['Speed limit, turn-rate limit', '0.22 m/s, 0.8 rad/s'],
        ['Slack penalty', '10^4 per unit'],
        ['Cost weights', 'q_position 1, q_terminal 1, r_input 0.01 (on input changes)'],
        ['Delay compensation, hold, stale odometry', '1 tick; hold up to 3 failed solves; stop if odometry older than 0.5 s'],
        ['Solve time, 95th percentile, N = 20 / 40 / 60', '59 / 174 / 367 ms'],
        ['Fit window', '1.0 s = 10 samples; noise 2 cm; speed std 0.28 m/s (two points) against 0.022 m/s (fit)'],
    ]],
    ['Scenarios 1 and 2', [
        ['Narrowest gap passed, one disc / three discs', '0.60 m / 0.30 m (proposal target 0.30 m)'],
        ['Three discs at 0.30 m', 'goal in 9.08 s, +0.050 m each side, speed dips to 0.12 m/s at 3.8 to 5.3 s'],
        ['One disc at 0.30 m', 'stops at x = 0.687 m, 3.48 s, 1.31 m short, +0.061 m'],
        ['Rings meet the centre line', 'x = 0.702 m (ring radius 0.389 m)'],
        ['0.28 m gap', 'three discs stop, 1.25 m short, +0.037 m'],
        ['Circle: path error, clearance (one / three)', '0.207 / 0.075 m; +0.089 / +0.011 m'],
        ['Eight: path error, clearance (one / three)', '0.302 / 0.027 m; +0.025 / +0.043 m'],
        ['Zero-margin graze (three discs, circle)', '-2.1 mm at 18.6 s; odometry 2.7 cm off; later 1.03 m'],
        ['Open corridor 0.60 m', '8.9 s'],
    ]],
    ['Scenario 3', [
        ['Obstacle', 'r = 0.10 m from (1.0, 1.2) at 0.30 m/s towards -y; crosses y = 0 at 3.99 s'],
        ['With its future', '3 of 3 passed; smallest +0.049, +0.048, +0.056 m at 5.17 to 5.20 s; goal in 11.4 to 11.5 s'],
        ['Its timeline', '1.8 s first reaction; stop 3.42 s at x = 0.70 m; heading -35 / -61 / -90 deg at 3.4 / 3.98 / 4.7 s'],
        ['Clearance at the crossing', '0.083 to 0.088 m'],
        ['Only its position now', '3 of 3 touched; -0.008, -0.007, -0.006 m; below zero 0.71 / 0.51 / 0.48 s'],
        ['Its timeline', '3.16 s first reaction (obstacle y 0.23 to 0.24); stop 3.3 s at x = 0.69; contact 3.47 to 3.54 s'],
        ['After the contact', 'true heading 304 to 547 deg in total; ends 1.04 / 0.99 / 1.59 m short; odometry 1.01 / 0.96 / 1.57 m off'],
        ['Body disturbance at the contact', 'roll 2.3 deg, pitch 5.6 deg, rise about 4 mm'],
        ['Solve time 3 to 6 s, median', '53 to 54 ms with its future, 60 to 72 ms without, 30 ms otherwise'],
        ['Desk prediction', '+0.044 m with its future, -0.041 m without'],
    ]],
    ['Scenario 4', [
        ['Ball', 'from (1.2, -1.2) at (0.05, 0.20) m/s = 0.206 m/s; robot 7 percent faster'],
        ['Fit: first within 0.2 m', '8.9, 13.9, 12.9 s (hold: never)'],
        ['Mean distance, last 5 s', 'fit 0.138, 0.210, 0.200 m (0.183 m); hold 0.341, 0.326, 0.301 m (0.323 m)'],
        ['Behind the ball at 8 s', 'fit 0.19, 0.26, 0.25 m; hold 0.40, 0.39, 0.36 m'],
        ['Desk prediction', 'fit 0.142 m (within 0.2 m at 8.6 s), hold 0.313 m (never)'],
        ['First ball (moving away, 0.12 m/s)', '0.27 m against 0.29 m: no difference'],
    ]],
    ['Odometry and runs', [
        ['Odometry error against truth, largest over a run', 's1 1.9 to 3.3 cm, s2 1.4 to 2.4 cm, s3 with future 1.9 to 3.5 cm, s4 2.1 to 8.0 cm'],
        ['Runs', '16 in scenarios 1 and 2 (8 pairs); 6 in scenario 3 and 6 in scenario 4 (3 each mode)'],
        ['Desktop against laptop', 'within about 1 cm on the runs repeated'],
        ['Demo video', '2 min 10 s, six pairs, drawn at the odometry pose'],
    ]],
]

# ------------------------------------------------------------------ the question bank

# area, who, question, answer. "dont" lists what not to say.
Q = [
    # ---- problem and scope
    ('Problem and scope', 'group', 'What problem did you solve, and why does it matter?',
     'In Lab 2 our MPC treated the robot as one disc of 0.105 m and every obstacle as still. We wanted a robot that '
     'carries a plank of 0.50 by 0.20 m, and obstacles that move, because a real floor has people and machines that '
     'cross it. One disc around the plank has a radius of 0.269 m and would refuse a 0.30 m gap that the plank fits '
     'through. So the problem is a body that is not round and an environment that is not still.'),
    ('Problem and scope', 'group', 'What were your research questions, and what are the answers?',
     'One: does a chain of discs let the robot use gaps that one disc rejects? Yes: three discs pass 0.30 m, one disc '
     'needs 0.60 m of the gaps we ran. Two: does knowing where an obstacle (or the goal) will be help? Yes in our two '
     'cases: with its future the plank passed 3 of 3 with +0.048 to +0.056 m, and with only its position it touched 3 '
     'of 3. The fit got within 0.2 m of the ball in 3 of 3 runs and the hold in none.'),
    ('Problem and scope', 'group', 'Why simulation only?',
     'The proposal said Gazebo only. We needed the same run repeated with the same obstacle timing, and the true '
     'distance measured every time, and a real floor gives neither. The limit is that wheel slip, the delay of a real '
     'robot and sensor noise are only what Gazebo models.'),
    ('Problem and scope', 'group', 'What changed against the proposal?',
     'The first proposal was an articulated vehicle that bends in the middle, with three members. Version 2 replaced it '
     'with the plank on the Burger, with two members, and we ran all four of its scenarios. Scenario 1b\'s obstacle '
     'moved from (0, 0.25) to (0, 0.36) with r = 0.08 m because the robot\'s start was inside the one-disc keep-out. '
     'The 2 cm margin, the extra 0.03 m for a moving obstacle and the noise on the ball are new.'),
    ('Problem and scope', 'group', 'Which parts did not work, and how did that change your plan?',
     'The first Gazebo check of Lab 2\'s slalom never moved, because the goal was published before the node was up. The '
     'first moving goal showed almost no difference between the modes, so we changed the geometry. The graze in '
     'scenario 1 led to the margin, and the Gazebo window tripled the solve time, so timed runs are headless. We could '
     'not explain the continued turning after the contact in scenario 3.'),
    # ---- fundamentals
    ('Fundamentals', 'both', 'Explain the model. Why can the plank not slide through sideways?',
     'The robot is a unicycle: x_dot = v cos(theta), y_dot = v sin(theta), theta_dot = omega, with v and omega as '
     'inputs. It has two wheels and cannot move sideways, which is the non-holonomic constraint of Lecture 3. So the plank '
     'lies along the heading and presents 0.50 m across it. To pass a gap it has to drive in line with the gap.'),
    ('Fundamentals', 'both', 'What is MPC, and why is only the first input sent?',
     'At every tick the controller solves an optimisation over the next N = 20 steps of 0.1 s, which is 2.0 s, and '
     'sends only the first input. Then the next tick solves again from the new measurement. The rest of the plan '
     'is a prediction that will be wrong a little, and the repeated solve corrects it. That is feedback.'),
    ('Fundamentals', 'both', 'What is the cost function?',
     'The squared distance to the goal, summed over the horizon with weight 1, and again at the last step with weight '
     '1, plus 0.01 times the change in the inputs, for smoothness. Everything else is a constraint: the input limits '
     '(0 to 0.22 m/s, 0.8 rad/s), the keep-outs and the box.'),
    ('Fundamentals', 'both', 'What is a time-varying parameter, and why do you use it?',
     'A TVP is a number the solver reads that we overwrite before every solve, one value for each step of the horizon. '
     'Rebuilding the solver takes seconds and a tick is 0.1 s, so anything that changes must be a TVP. The goal was one '
     'in Lab 2. We made the obstacle centre one too, and in scenario 4 the goal is filled from the estimate.'),
    ('Fundamentals', 'both', 'Why soft constraints, and what is the penalty?',
     'A soft constraint adds a slack variable that costs 10^4 per unit. When a plan that keeps clear exists, the slack '
     'is zero and it behaves like a hard constraint. When none exists, the solver still returns something. In Lab 2 a '
     'hard bound on a measured state made the first solve infeasible when odometry put the robot outside it, so we '
     'made the box soft too. It is not a guarantee: it allows a small violation when that is cheap.'),
    ('Fundamentals', 'both', 'Why discs, why three, and how did you get the radius?',
     'A disc gives a smooth quadratic constraint that IPOPT handles well. A rectangle has corners. We cut the plank '
     'into n slices and put a disc on each, just big enough to cover the slice\'s corners: r_n = sqrt((L/2n)^2 + '
     '(W/2)^2). In words: half the diagonal of a slice. That gives 0.269, 0.160 and 0.130 m. Three is the smallest n '
     'that fits the proposal\'s 0.30 m gap, and each extra disc saves less width.'),
    ('Fundamentals', 'both', 'Write the keep-out constraint and explain it.',
     '(r_obstacle + r_disc + margin)^2 - ((c_x - o_x)^2 + (c_y - o_y)^2) <= 0, with c = (x + d cos theta, y + d sin theta). '
     'In words: every disc centre must stay farther from the obstacle\'s centre than the two radii plus the margin. '
     'The disc centres turn with the heading, so each one is a short expression in x, y and theta. Both sides are '
     'squared, so there is no square root.'),
    ('Fundamentals', 'both', 'Why is the box shrunk by 0.269 m?',
     'It is the radius the plank sweeps when the robot turns on the spot: half its diagonal. If the axle point stays '
     'inside a box shrunk by that much, the plank fits inside the real box at any heading.'),
    ('Fundamentals', 'both', 'What is delay compensation?',
     'The command decided now is executed one tick later, so we first predict where the robot will be after the '
     'last command, then solve from there. The same one-tick shift is in the obstacle prediction: o(k) = o_now + v '
     '(d + k) dt, with d = 1. We kept it from Lab 2.'),
    ('Fundamentals', 'both', 'How do you handle failed solves and old odometry?',
     'We hold the last command through up to three failed solves, and stop if odometry is older than 0.5 s. Both '
     'are from Lab 2.'),
    ('Fundamentals', 'both', 'How does the moving-obstacle prediction work, and how do the two modes differ?',
     'The obstacle centre is a TVP. With its future the centre at step k is its position now plus its velocity times '
     '(d + k) times dt, a straight line. With only its position now the centre is its position now for every step, so '
     'the obstacle looks still. A pair of runs differs in this one node parameter. The node knows the velocity because '
     'we chose the path, which is the assumption in the proposal.'),
    ('Fundamentals', 'both', 'How does the goal estimator work, and why least squares?',
     'The controller sees the ball with 2 cm of noise and keeps the last 1.0 s, 10 samples. It fits a line for x and '
     'for y by least squares and extends it across the horizon. In words: v is the slope of the best line through '
     'position against time. Differencing the last two points gives a speed with a standard deviation of 0.28 m/s, '
     'more than the ball\'s own 0.206 m/s, and the fit over ten points gives 0.022 m/s.'),
    ('Fundamentals', 'both', 'Why not a Kalman filter?',
     'The ball moves at a constant velocity, so a line fit is exact for it and needs no model of the noise. For a ball '
     'that turns, a constant velocity line is wrong, and the Kalman filter of Lecture 8 with a motion model would be the '
     'next step. We did not build it.'),
    ('Fundamentals', 'both', 'Why is the mover margin 0.03 m on top of 0.02 m?',
     'With its future the optimiser passes as close as the constraint allows: at the desk 1 to 2 cm, and odometry was '
     '1.4 to 3.5 cm off in scenarios 1 to 3. So it got more room, 0.28 m in all. The measured clearance, +0.048 to '
     '+0.056 m, is the 0.05 m that the two margins add up to.'),
    # ---- evaluation
    ('Evaluation', 'group', 'How did you grade the runs, and why from the ground truth?',
     'From Gazebo\'s ground-truth pose of the robot against the exact 0.50 by 0.20 m rectangle, which the controller '
     'never reads. The controller believes in discs and the world contains a rectangle, so grading with disc '
     'distances would ask the model whether the model was right. Odometry would hide its own drift.'),
    ('Evaluation', 'group', 'How is clearance defined?',
     'Move the obstacle centre into the plank\'s frame: p = R(theta)^T (o - (x, y)). Take the nearest point of the '
     'rectangle: q = clamp(p, half sizes). Clearance = |p - q| - r_obstacle. A value of 0 or less is contact. For '
     'a moving obstacle we use its ground-truth pose at the instant of each robot sample.'),
    ('Evaluation', 'group', 'Is three runs enough?',
     'It is a small sample. The verdict was the same in all three runs of every mode, and the clearances with its '
     'future differed by 8 mm. It does not change the verdict for scenario 3, and it is a small sample for the size of '
     'the gain in scenario 4. Scenarios 1 and 2 were also repeated on the desktop, and agree to within about 1 cm.'),
    ('Evaluation', 'group', 'Why headless?',
     'The Gazebo window roughly triples the solve time, so a run with the window would not show what the controller '
     'does at 0.1 s. So the timed runs are headless and the video is replayed in RViz from the recorded bags.'),
    ('Evaluation', 'group', 'How well did the desk simulation predict Gazebo?',
     'The verdicts agreed. Scenario 3: +0.044 m with its future and -0.041 m without at the desk, against +0.048 to '
     '+0.056 m and contact in Gazebo. Scenario 4: fit 0.142 m and hold 0.313 m at the desk, against 0.183 m and 0.323 '
     'm. The desk has no physics and no acceleration limit.'),
    ('Evaluation', 'group', 'What does the video show, and what should we not read into it?',
     'Six pairs, baseline on the left, the new idea on the right, replayed in RViz from the bags. The plank is drawn at '
     'the pose from /odom. That is within 5 cm of the ground truth in eleven of the twelve runs. In scenario 3 with '
     'only its position now it is up to 1 m off after the contact, so the clip shows a robot that seems to reach the '
     'goal while the real one stopped 1.04 m short. The numbers are from the ground truth.',
     'Do not say the video shows what really happened after the contact.'),
    ('Evaluation', 'group', 'How good was odometry?',
     'Largest position error over a run: 1.9 to 3.3 cm in scenario 1, 1.4 to 2.4 cm in scenario 2, 1.9 to 3.5 cm in '
     'scenario 3 with its future, 2.1 to 8.0 cm in scenario 4. After the contact without the future, about 1 m.'),
    # ---- results and dynamics
    ('Results', 'both', 'Why did the one-disc robot stop at the 0.30 m gap?',
     'Its keep-out ring around each post is 0.389 m, and the post centres are 0.25 m from the line, so the rings meet '
     'the centre line at x = 0.702 m. It stopped at x = 0.687 m, within 1.5 cm of that. Going on would cost slack '
     'at 10^4 per unit.'),
    ('Results', 'both', 'Why does three discs pass at 0.30 m and stop at 0.28 m, when the plank fits both?',
     'The keep-out with the margin needs 2 x (0.1302 + 0.02) = 0.3003 m. At 0.30 m it is 0.3 mm short and the robot '
     'passes with dips in speed to 0.12 m/s. At 0.28 m it is 2 cm short and the robot stops. The real plank has 0.04 m on '
     'each side at 0.28 m: the discs and the margin are conservative. The 0.3 mm is derived, not measured.',
     'Do not say that we measured the slack. We did not.'),
    ('Results', 'both', 'Why did the circle with three discs have so little clearance (+0.011 m)?',
     'Three discs follow the circle closely, so they pass the obstacle with only the margin to spare, and the real '
     'clearance is at least about the margin if the constraint holds. One disc swings 0.207 m wide and keeps +0.089 m. '
     'That is the price of staying on the path, and it was a contact in no run once the margin was in.'),
    ('Results', 'both', 'Why did the robot turn in scenario 3, when you expected it to wait?',
     'It also waited: it stood at x = 0.70 m from 3.4 s. And it kept turning in place: heading -35 degrees at 3.4 s, '
     '-61 degrees when the obstacle crossed, -90 degrees at 4.7 s. Our reading is that a plank lying along the obstacle\'s '
     'path reaches less far across it, which is cheapest for the keep-out. We did not test that.',
     'Do not say it turned "to face the obstacle", or that the turn was complete at the crossing.'),
    ('Results', 'both', 'Why did it touch with only its position now?',
     'It reacted late, at 3.16 s, when the obstacle\'s current position reached the keep-out: the front disc was 0.29 '
     'm from it against a keep-out of 0.28 m. The obstacle was coming at 0.30 m/s, and the stopped plank\'s front end '
     'at x = 0.94 m was already inside its lane (0.90 to 1.10 m). With its future the controller reacted at 1.80 s, '
     '2.2 s before the crossing. The distance figures are derived from the bags and the geometry.'),
    ('Results', 'both', 'What happened after the contact?',
     'In all three runs the true heading kept turning clockwise, 304 to 547 degrees in total, also while the '
     'commanded turn rate had the other sign (run 1, from 5.5 s). Odometry follows the wheels and did not follow it: '
     'in run 1 the difference was 28 degrees at 5 s, 113 at 6 s and 213 at 7 s. The robot drove away from the goal and '
     'stopped 1.04, 0.99 and 1.59 m short. We do not know why the true heading kept turning, and we did not test '
     'whether the wheels slipped.',
     'Never say "the wheels slipped" as a fact.'),
    ('Results', 'both', 'What did the fit change in scenario 4?',
     'Both robots drive at the speed limit for 99 percent of the run and line up with the ball\'s path by 8 s. The fit '
     'trails 0.19 to 0.26 m behind at 8 s and the hold 0.36 to 0.40 m. The fit got within 0.2 m in every run and the '
     'hold never did, and the mean distance over the last 5 s is 0.183 m against 0.323 m, about 43 percent smaller. The '
     'gain is a smaller lag and not a different path.',
     'Do not say the fit "cuts across".'),
    ('Results', 'both', 'Why is the gain in scenario 4 only 43 percent?',
     'The robot is only 7 percent faster than the ball (0.22 against 0.206 m/s), so after the first 8 s both close the '
     'gap by only about 0.01 m/s. The estimate helps the robot aim, and speed decides how fast it catches up.'),
    ('Results', 'both', 'Why did the first moving goal show nothing?',
     'It moved slowly away at 0.12 m/s, and the robot is faster, so it caught up whatever it believed: 0.27 m against '
     '0.29 m at the desk. We changed the geometry to the crossing one, where the desk gave 0.142 m against 0.313 m.'),
    ('Results', 'both', 'Is the solve time a problem?',
     'Medians are 22 to 33 ms in scenarios 1 and 2 and up to 72 ms during an avoidance in scenario 3. A few single '
     'ticks went above 100 ms: up to 116 ms with its future (one run) and 127 to 248 ms in the runs that touched. We did '
     'not investigate what that does to the behaviour. N = 40 and 60 were too slow for the tick: 174 and 367 ms at the '
     '95th percentile.'),
    ('Results', 'both', 'What was the zero-margin graze, and what did you do?',
     'In scenario 1 with three discs and no margin the real plank grazed the obstacle by 2.1 mm, 18.6 s after the '
     'first command, while odometry was 2.7 cm off the truth. The desk simulation had predicted +3.7 mm. We added '
     '0.02 m to every keep-out. It costs 4 cm of gap.'),
    # ---- limits and learning
    ('Limits and learning', 'both', 'What are the limits of your work?',
     'Everything is simulation. The controller trusts odometry, which was 1.4 to 3.5 cm off in scenarios 1 to 3, up to '
     '8 cm in scenario 4 and about 1 m off after a contact. The discs are conservative. The obstacle and the ball move '
     'in straight lines at constant speeds, so the fit is exact for the ball. One moving obstacle was run. Three runs '
     'of each mode are a small sample.'),
    ('Limits and learning', 'both', 'What did you learn?',
     'Five things. A measurement has to be independent of the thing measured: the ground truth caught a graze that the '
     'discs called clear. A soft constraint with a large linear penalty did not deadlock where a hard bound did in Lab '
     '2. Simulation hides timing, as the window and the late goal showed. A margin is a trade: 2 cm bought robustness '
     'and cost the 0.28 m gap. And a comparison needs a situation that can tell the options apart.'),
    ('Limits and learning', 'both', 'What would you do next?',
     'Try a goal that turns, with the Kalman filter of Lecture 8. Find out why the true heading kept turning after the '
     'contact. Run more than one moving obstacle: the code takes a list of movers, and we ran one.'),
    ('Limits and learning', 'both', 'How does the project connect to the lectures and labs?',
     'Lecture 4: the unicycle model and MPC, the controller. Lecture 3: the non-holonomic constraint. Lectures 5 to 7: '
     'navigation and map inflation, the idea behind our keep-out. Lecture 10: least squares for the fit. Lecture 8: the '
     'Kalman filter, the alternative. Lab 2: the controller we extended. Lab 3: the inflation radius that our margin '
     'follows. Lab 4: estimating pose when odometry drifts, which is what we saw after the contact.'),
    # ---- individual
    ('Individual', 'individual', 'What was your part, in your own words?',
     'Dominic: I came up with the project outline, using Lab 2 as the basis. We discussed how to turn the idea into '
     'code plans and implementation details. Then I worked on the code: the controller, the scenarios, the Gazebo '
     'worlds, the runs and the analysis. Abdalrahman: he took part in the discussion of the code plans and '
     'implementation details, and took the report-writing steps, defining the structure and the presentation details '
     'together with me.'),
    ('Individual', 'individual', 'Pick one thing you wrote and walk us through it.',
     'Pick one before the day and be able to explain every line. Good candidates: the keep-out loop in build_TBmpc (for each '
     'disc and obstacle, a soft constraint on the squared distance), predict_mover (two modes, one line each), '
     'estimate_goal (least squares slope, the fitted line at the latest sample, extended over the horizon), or '
     'rectangle_clearance (the three lines of grading).'),
    ('Individual', 'individual', 'What would happen if you changed one parameter: the penalty, N, the margin, r_input?',
     'Measured: margin 0 gave a graze of 2.1 mm; N = 40 and 60 were too slow (174 and 367 ms). Not tested: the '
     'penalty and r_input. Say which are which. A smaller penalty would let the solver accept larger violations, and '
     'a larger r_input would make the motion smoother and slower to react: those are reasoning, not runs.',
     'Do not present the untested ones as results.'),
    ('Individual', 'individual', 'How is the report built, and which figure is the most important?',
     'It follows the proposal: problem and questions, block diagram, the controller, how we check a run, results for '
     'scenarios 1 to 4, what changed and what did not work, limitations and learning, and the links to lectures and labs. '
     'The most important figure is the one with the real clearance against the gap in scenario 2, because it answers the '
     'first research question; for the second it is Figure 3, the paths and clearance of scenario 3.'),
    # ---- traps
    ('Traps', 'both', 'So you have proven that knowing the future helps?',
     'We have evidence in one setup: one obstacle, a straight line at constant speed, a path we chose, three runs of '
     'each mode, and a velocity given to the controller. With its future the plank passed 3 of 3, and without it '
     'touched 3 of 3. It is not a proof for obstacles in general.'),
    ('Traps', 'both', 'Did the wheels slip after the contact?',
     'We do not know. The true heading kept turning, odometry did not follow, and we did not investigate the cause. '
     'To find out we would compare the wheel speeds with the true motion and look at the contact in Gazebo.',
     'Do not say yes or no.'),
    ('Traps', 'both', 'Could the three-disc plank pass the 0.28 m gap?',
     'Not with our 0.02 m margin: the keep-out needs 0.30 m. The real plank has 0.04 m on each side. With a margin '
     'of 0.01 m or less the keep-out would fit by the numbers (2 x (0.1302 + 0.01) = 0.280 m), but with zero margin we '
     'saw a graze in scenario 1, so we did not try. Derived, not run.'),
    ('Traps', 'both', 'What if two obstacles cross at once?',
     'The code takes a list of movers and makes one constraint per disc per mover, so it should work. We ran only '
     'one moving obstacle, and with more the solve time would grow, because each mover adds three constraints per step '
     'and the solve time already peaked at 72 ms with one. We did not test it.'),
    ('Traps', 'both', 'Your robot touched the obstacle. Does that not mean the controller failed?',
     'In the baseline mode, yes: with only its position now the plank touched 3 of 3 times, by 6 to 8 mm. That is the '
     'comparison. With its future it did not touch, and the baseline is there to show the difference. After the contact '
     'we cannot trust the run: the true heading and odometry diverged and the robot ended 1 to 1.6 m short.'),
]


def image_uri(name):
    with open(os.path.join(PLOTS, name), 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')


def main():
    data = dict(
        keywords=KEYWORDS,
        gapQuestions=GAP_QUESTIONS,
        claims=[dict(claim=c, breaks=b) for c, b in CLAIMS],
        cards=CARDS,
        numbers=[dict(group=g, rows=r) for g, r in NUMBERS],
        questions=[dict(id='q%d' % i, area=a, who=w, q=q, a=ans, dont=(rest[0] if rest else ''))
                   for i, (a, w, q, ans, *rest) in enumerate(Q, start=1)],
        images={k: image_uri(v) for k, v in IMAGES.items()},
    )

    with open(os.path.join(HERE, 'defence_template.html'), encoding='utf-8') as f:
        page = f.read()

    out = os.path.join(HERE, 'Project Defence Guide.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page.replace('{{DATA}}', json.dumps(data, ensure_ascii=False)))
    print('wrote', out, '(%d kB)' % (os.path.getsize(out) // 1024), '-', len(Q), 'questions,', len(CARDS), 'cards')


if __name__ == '__main__':
    main()
