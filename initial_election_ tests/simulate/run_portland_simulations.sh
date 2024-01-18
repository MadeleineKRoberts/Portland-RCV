#!/bin/bash
#SBATCH --job-name=simulate   ##Current Directory Name
#SBATCH --time=4-00:00:00   
#SBATCH --nodes=4 
#SBATCH --cpus-per-task=16
#SBATCH --ntasks-per-node=1
#SBATCH --mem=64000
#SBATCH --output=simulate.%j.out   
#SBATCH --error=simulate.%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=mrober17@tufts.edu    

module load anaconda/2021.05

source activate /cluster/tufts/mggg/jgibso04/condaenv/initial_election_tests # ask jack if this is correct path 

python3 simulate_elections.py --alpha 1 0.5 2 --alpha_cc 0.5 1 2 --candidates 3 3 3 5 5 3 2 6 6 2

conda deactivate
