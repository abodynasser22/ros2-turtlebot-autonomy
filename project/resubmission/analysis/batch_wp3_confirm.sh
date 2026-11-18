#!/usr/bin/env bash
# WP3 confirmation: the most promising screening settings, three runs each, both modes of S3.
#     bash batch_wp3_confirm.sh > ../bags/batch_wp3_confirm.log 2>&1
cd "$(dirname "$0")"
source ../env.sh
for pv in max_angular_velocity:1.2 max_angular_velocity:2.0 safety_margin:0.05; do
  p=${pv%%:*}; v=${pv#*:}
  for i in 1 2 3; do
    for m in future now; do
      python3 run_headless_stats.py --outdir ../bags/wp3c s3 three wp3c_${p}_${v}_${m}_$i 17 \
        -p prediction:=$m -p $p:=$v || echo "FAILED: $p $v $m $i"
    done
  done
done
echo BATCH DONE
