#!/bin/bash
#SBATCH --job-name=vsc_4
#SBATCH --partition=standard-g
#SBATCH --account=project_462000189

#SBATCH --time=2-00:00:00 

#SBATCH --ntasks=2 

#SBATCH --cpus-per-task=8 

#SBATCH --gpus-per-task=4 

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK # 

export MPICH_GPU_SUPPORT_ENABLED=1 # 

./vscode
