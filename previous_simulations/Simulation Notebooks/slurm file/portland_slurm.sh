#!/bin/bash 

alpha_poc_matrix=("1 1 1" \
                  "2 2 2" )

alpha_wp_matrix=("1 1 1" \
                 "2 2 2" )

alpha_wc_matrix=("1 1 1" \
                 "2 2 2" )

cohesion_poc_matrix=("0.8 0.1 0.1" \
                     "0.4 0.3 0.3" \
                     "0.8 0.1 0.1" \
                     "0.8 0.1 0.1" \
                     "0.45 0.45 0.1" \
                     "0.6 0.3 0.1")

cohesion_wp_matrix=("0.1 0.8 0.1" \
                    "0.3 0.4 0.3" \
                    "0.1 0.45 0.45" \
                    "0.8 0.1 0.1" \
                    "0.45 0.45 0.1" \
                    "0.3 0.6 0.1")

cohesion_wc_matrix=("0.1 0.1 0.8" \
                    "0.3 0.3 0.4" \
                    "0.1 0.45 0.45" \
                    "0.1 0.1 0.8" \
                    "0.1 0.1 0.8" \
                    "0.1 0.1 0.8")

candidates_matrix=("2 5 5" \
                   "2 8 2" \
                   "6 4 4" \
                   "6 7 1" \
                   "5 3 2" \
                   "5 4 1" \
                   "3 4 4" \
                   "3 7 1" )

n_elections=1000

output_dir="Port_outputs"
log_dir="Port_logs"

mkdir -p "${output_dir}"
mkdir -p "${log_dir}"

for i in "${!alpha_poc_matrix[@]}"; do
    for j in "${!alpha_wp_matrix[@]}"; do
        for k in "${!alpha_wc_matrix[@]}"; do
            alpha_poc="${alpha_poc_matrix[$i]}"
            alpha_wp="${alpha_wp_matrix[$j]}"
            alpha_wc="${alpha_wc_matrix[$k]}"
            
            # Cohesion parameters are grouped by their index, so we loop through them separately
            for l in "${!cohesion_poc_matrix[@]}"; do
                cohesion_poc="${cohesion_poc_matrix[$l]}"
                cohesion_wp="${cohesion_wp_matrix[$l]}"
                cohesion_wc="${cohesion_wc_matrix[$l]}"
                
                for candidates in "${candidates_matrix[@]}"; do
                    echo "==================="
                    # Submit job with sbatch, passing parameters to the script
                    sbatch ./port_run.sh "$alpha_poc" "$alpha_wp" "$alpha_wc" "$cohesion_poc" "$cohesion_wp" "$cohesion_wc" "$candidates" $n_elections $output_dir $log_dir
                done
            done
        done
    done
done


