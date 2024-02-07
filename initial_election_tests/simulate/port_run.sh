#!/bin/bash

#SBATCH --job-name=port_elect_sim_3
#SBATCH --time=48:00:00
#SBATCH --nodes=4
#SBATCH --cpus-per-task=2
#SBATCH --ntasks-per-node=1
#SBATCH --mem=30G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mrober17@tufts.edu


alpha_poc_params=$1
alpha_wp_params=$2
alpha_wc_params=$3
cohesion_poc_params=$4
cohesion_white_progressive_params=$5
cohesion_white_conservative_params=$6
candidates=$7
num_elections=$8
output_dir=$9
log_dir=${10}

base_log_file="${candidates}_${alpha_poc_params}_${alpha_wp_params}_${alpha_wc_params}_${cohesion_poc_params}_${cohesion_white_progressive_params}_${cohesion_white_conservative_params}_with_${num_elections}_sims"
log_file="${log_dir}/${base_log_file}.log"

echo --candidates "$candidates" \
        --alpha_poc_params "$alpha_poc_params" \
        --alpha_wp_params "$alpha_wp_params" \
        --alpha_wc_params "$alpha_wc_params" \
        --cohesion_poc_params "$cohesion_poc_params" \
        --cohesion_white_progressive_params "$cohesion_white_progressive_params" \
        --cohesion_white_conservative_params "$cohesion_white_conservative_params" \
        --num_elections "$num_elections"

{
    python simulate_elections_zbz.py \
        --candidates "$candidates" \
        --alpha_poc_params "$alpha_poc_params" \
        --alpha_wp_params "$alpha_wp_params" \
        --alpha_wc_params "$alpha_wc_params" \
        --cohesion_poc_params "$cohesion_poc_params" \
        --cohesion_white_progressive_params "$cohesion_white_progressive_params" \
        --cohesion_white_conservative_params "$cohesion_white_conservative_params" \
        --num_elections "$num_elections"
} > "${output_dir}/${base_log_file}.txt"

# Record resource usage

echo $log_file
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU >> "$log_file" 2>> "$log_file"
