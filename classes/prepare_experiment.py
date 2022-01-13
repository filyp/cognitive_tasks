import random

from psychopy import logging


def prepare_trials(block, stimulus):
    # logging.data(f"{block=}")
    # logging.data(f"{stimulus=}")
    # logging.flush()

    all_trials = []

    stimulus_dict = {stim["name"]: stim for stim in stimulus}

    if "number_of_congruent_trials" in block:
        number_of_congruent_trials = block["number_of_congruent_trials"]
        assert number_of_congruent_trials % 2 == 0  # number_of_congruent_trials must be even
        for _ in range(number_of_congruent_trials // 2):
            trial = dict(
                type="congruent",
                target=stimulus_dict["congruent_lll"],
            )
            all_trials.append(trial)

            trial = dict(
                type="congruent",
                target=stimulus_dict["congruent_rrr"],
            )
            all_trials.append(trial)

    if "number_of_incongruent_trials" in block:
        number_of_incongruent_trials = block["number_of_incongruent_trials"]
        assert number_of_incongruent_trials % 2 == 0  # number_of_incongruent_trials must be even
        for _ in range(number_of_incongruent_trials // 2):
            trial = dict(
                type="incongruent",
                target=stimulus_dict["incongruent_lrl"],
            )
            all_trials.append(trial)

            trial = dict(
                type="incongruent",
                target=stimulus_dict["incongruent_rlr"],
            )
            all_trials.append(trial)

    random.shuffle(all_trials)
    return all_trials
