import os
import sys
import itertools

dry_run = '--dry-run' in sys.argv

if not os.path.exists("slurm_logs"):
    os.makedirs("slurm_logs")

if not os.path.exists("slurm_scripts"):
    os.makedirs("slurm_scripts")

code_dir = '/private/home/willwhitney/code'

basename = "handful-seeds-xvel"
grids = [
    {
        "env": [
            "swimmer",
            "visiblehalfcheetah",
        ],
        "seed": [0, 1, 2, 3, 4],
    },


]

jobs = []
for grid in grids:
    individual_options = [[{key: value} for value in values]
                          for key, values in grid.items()]
    product_options = list(itertools.product(*individual_options))
    jobs += [{k: v for d in option_set for k, v in d.items()}
             for option_set in product_options]

if dry_run:
    print("NOT starting {} jobs:".format(len(jobs)))
else:
    print("Starting {} jobs:".format(len(jobs)))

merged_grid = {}
for grid in grids:
    for key in grid:
        merged_grid[key] = [] if key not in merged_grid else merged_grid[key]
        merged_grid[key] += grid[key]
varying_keys = {key for key in merged_grid if len(set(merged_grid[key])) > 1}

for job in jobs:
    jobname = basename
    flagstring = ""
    for flag in job:
        if isinstance(job[flag], bool):
            if job[flag]:
                flagstring = flagstring + " -" + flag
                if flag in varying_keys:
                    jobname = jobname + "_" + flag + str(job[flag])
            else:
                print("WARNING: Excluding 'False' flag " + flag)
        else:
            flagstring = flagstring + " -" + flag + " " + str(job[flag])
            if flag in varying_keys:
                jobname = jobname + "_" + flag + str(job[flag])
    flagstring = flagstring + " -logdir " + "log/" + jobname

    slurm_script_path = 'slurm_scripts/' + jobname + '.slurm'
    slurm_script_dir = os.path.dirname(slurm_script_path)
    os.makedirs(slurm_script_dir, exist_ok=True)

    slurm_log_dir = 'slurm_logs/' + jobname
    os.makedirs(os.path.dirname(slurm_log_dir), exist_ok=True)

    true_source_dir = code_dir + '/handful-of-trials'
    job_source_dir = code_dir + '/handful-of-trials-clones/' + jobname

    os.makedirs(job_source_dir, exist_ok=True)
    os.system('cp -R dmbrl/ ' + job_source_dir)
    os.system('cp -R scripts/ ' + job_source_dir)
    os.system('cp *.py ' + job_source_dir)

    jobcommand = "python {}/scripts/mbexp.py{}".format(job_source_dir, flagstring)

    job_start_command = "sbatch " + slurm_script_path
    # jobcommand += " --restart-command '{}'".format(job_start_command)

    print(jobcommand)
    with open(slurm_script_path, 'w') as slurmfile:
        slurmfile.write("#!/bin/bash\n")
        slurmfile.write("#SBATCH --job-name" + "=" + jobname + "\n")
        slurmfile.write("#SBATCH --open-mode=append\n")
        slurmfile.write("#SBATCH --output=slurm_logs/" +
                        jobname + ".out\n")
        slurmfile.write("#SBATCH --error=slurm_logs/" + jobname + ".err\n")
        slurmfile.write("#SBATCH --export=ALL\n")
        slurmfile.write("#SBATCH --signal=USR1@600\n")
        slurmfile.write("#SBATCH --time=3-00\n")
        # slurmfile.write("#SBATCH -p dev\n")
        slurmfile.write("#SBATCH -p priority\n")
        slurmfile.write("#SBATCH -N 1\n")
        slurmfile.write("#SBATCH --mem=60gb\n")

        slurmfile.write("#SBATCH -c 8\n")
        slurmfile.write("#SBATCH --gres=gpu:1\n")

        # slurmfile.write("#SBATCH -c 40\n")
        # slurmfile.write("#SBATCH --constraint=pascal\n")

        slurmfile.write("cd " + true_source_dir + '\n')
        slurmfile.write("srun " + jobcommand)
        slurmfile.write("\n")

    if not dry_run:
        os.system(job_start_command + " &")
