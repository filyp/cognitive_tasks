# Cognitive tasks

This repository contains procedures for multiple cognitive psychology experiments:
- flanker task
- diamond decision task
- monetary incentive delay
- go no-go task

## Installation

First, make sure you have python3.6 or newer installed. Then, run in bash:

```bash
git clone https://github.com/filyp/cognitive_tasks.git
cd cognitive_tasks
python3 -m pip install -r requirements.txt
```

Instead of downloading the latest version of the procedures, you may want some older version, marked with some tag. For example, for tag `diamond_task_tested`, you can use this command instead:
```
git clone --branch diamond_task_tested https://github.com/filyp/cognitive_tasks.git
```

## Running

Go inside the `cognitive_tasks` folder and run:

```bash
python3 main.py config/{task you want to run}.yaml
```

For example:
```bash
python3 main.py config/diamond_task_C.yaml
```

See the folder `config` for all the available tasks and their versions. To create a new version of a task, just copy the `config/{task}.yaml` file and change the parameters.

To stop the procedure, press `F7` (or in older versions `Esc`).

All the output data will be saved in the `results` folder. Each version of a task has it's own subfolder, so if you modify some config file and run the procedure again, a new subfolder will be created for this version. The config file is copied into this subfolder, so you can be sure in which task version was the data collected.

## Behavioral analysis

There are scripts summarizing behavioral data (for some tasks) in `behavioral_analysis` folder. For example to run analysis for flanker task:
```bash
python3 behavioral_analysis/flankers.py results/{directory with results from your experiment}
```
