# Cognitive tasks

This repository contains procedures for multiple cognitive psychology experiments:
- flanker task
- diamond decision task
- monetary incentive delay

## Running

```bash
python main.py config/<task you want to run>.yaml
```

See the folder `config` for all the available tasks and their versions.

## Behavioral analysis

There are scripts summarizing behavioral data in `behavioral_analysis` folder. For example to run analysis for flanker task:
```
python behavioral_analysis/flankers.py results/<directory with results from your experiment>
```

## Dependencies

You need python3.6 or newer, and then run:
```
pip install -r requirements.txt
```
