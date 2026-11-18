#!/usr/bin/env bash
# WP3 screening (one run per value, both modes of S3) and WP4 horizon sweep (S3 and S4, three runs
# each). Headless, with /mpc_stats. A bag that already exists is skipped by the harness.
#     bash batch_wp3_wp4.sh > ../bags/batch_wp3_wp4.log 2>&1
cd "$(dirname "$0")"
source ../env.sh
run() { python3 run_headless_stats.py --outdir "$1" "${@:2}" || echo "FAILED: $*"; }

# WP3: parameter, two non-default values (the default is the middle value)
SCREEN="q_position:0.5 q_position:5.0 q_terminal:0.5 q_terminal:5.0 r_input:0.001 r_input:0.05
obstacle_penalty:5000.0 obstacle_penalty:50000.0 safety_margin:0.0 safety_margin:0.05
mover_margin:0.0 mover_margin:0.05 delay_steps:0 delay_steps:2
max_angular_velocity:1.2 max_angular_velocity:2.0"
run ../bags/wp3 s3 three wp3_default_now 17 -p prediction:=now
for pv in $SCREEN; do
  p=${pv%%:*}; v=${pv#*:}
  for m in future now; do
    run ../bags/wp3 s3 three wp3_${p}_${v}_${m} 17 -p prediction:=$m -p $p:=$v
  done
done

# WP4: horizon N at t_step 0.1 s
for N in 10 20 30 40; do
  for i in 1 2 3; do
    for m in future now; do
      run ../bags/wp4 s3 three wp4_N${N}_s3_${m}_$i 17 -p prediction:=$m -p n_horizon:=$N
    done
    for e in fit hold; do
      run ../bags/wp4 s4 three wp4_N${N}_s4_${e}_$i 17 -p goal_estimate:=$e -p noise_seed:=$i -p n_horizon:=$N
    done
  done
done
echo BATCH DONE
