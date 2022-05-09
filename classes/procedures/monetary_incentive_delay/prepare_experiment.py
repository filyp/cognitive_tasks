import math
import random

from psychopy import logging


def prepare_trials(block, stimulus):
    all_trials = []

    number_of_trials = block["number_of_trials"]
    cue_incentive_ratio = block["cue_incentive_ratio"]

    number_of_cue_incentive = math.ceil(number_of_trials * cue_incentive_ratio)
    number_of_cue_neutral = number_of_trials - number_of_cue_incentive

    logging.data(
        f"""
    Preparing trials:
        block={block}
        number_of_cue_incentive={number_of_cue_incentive}
        number_of_cue_neutral={number_of_cue_neutral}
    """
    )

    for _ in range(number_of_cue_incentive):
        all_trials.append(dict(cue=stimulus["cue_incentive"]))
    for _ in range(number_of_cue_neutral):
        all_trials.append(dict(cue=stimulus["cue_neutral"]))

    random.shuffle(all_trials)
    return all_trials
