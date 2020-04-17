#!/bin/bash
#
#SBATCH --partition=normal
#SBATCH --ntasks=1
# memory in MB
#SBATCH --mem=10024
#SBATCH --output=output/exp_%J_stdout.txt
#SBATCH --error=error/exp_%J_stderr.txt
#SBATCH --time=02:30:00
#SBATCH --job-name=capstone_exp
#SBATCH --mail-user=alan.lee-1@ou.edu
#SBATCH --mail-type=ALL
#SBATCH --chdir=/home/oucs4473022/capstone/capstone
#SBATCH --array=0-728
#
#################################################
source ~fagg/pythonenv/tensorflow/bin/activate
python cross_validation.py -exp_idx $SLURM_ARRAY_TASK_ID
