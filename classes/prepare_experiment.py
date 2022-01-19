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
        assert number_of_congruent_trials % 4 == 0  # it must be a multiple of 4
        for _ in range(number_of_congruent_trials // 4):
            all_trials.append(
                dict(
                    type="congruent",
                    cue=stimulus_dict["cue1"],
                    flankers=stimulus_dict["flankers_l"],
                    target=stimulus_dict["congruent_lll"],
                )
            )
            all_trials.append(
                dict(
                    type="congruent",
                    cue=stimulus_dict["cue1"],
                    flankers=stimulus_dict["flankers_r"],
                    target=stimulus_dict["congruent_rrr"],
                )
            )
            all_trials.append(
                dict(
                    type="congruent",
                    cue=stimulus_dict["cue2"],
                    flankers=stimulus_dict["flankers_l"],
                    target=stimulus_dict["congruent_lll"],
                )
            )
            all_trials.append(
                dict(
                    type="congruent",
                    cue=stimulus_dict["cue2"],
                    flankers=stimulus_dict["flankers_r"],
                    target=stimulus_dict["congruent_rrr"],
                )
            )

    if "number_of_incongruent_trials" in block:
        number_of_incongruent_trials = block["number_of_incongruent_trials"]
        assert number_of_incongruent_trials % 4 == 0  # it must be a multiple of 4
        for _ in range(number_of_incongruent_trials // 4):
            all_trials.append(
                dict(
                    type="incongruent",
                    cue=stimulus_dict["cue1"],
                    flankers=stimulus_dict["flankers_l"],
                    target=stimulus_dict["incongruent_lrl"],
                )
            )
            all_trials.append(
                dict(
                    type="incongruent",
                    cue=stimulus_dict["cue1"],
                    flankers=stimulus_dict["flankers_r"],
                    target=stimulus_dict["incongruent_rlr"],
                )
            )
            all_trials.append(
                dict(
                    type="incongruent",
                    cue=stimulus_dict["cue2"],
                    flankers=stimulus_dict["flankers_l"],
                    target=stimulus_dict["incongruent_lrl"],
                )
            )
            all_trials.append(
                dict(
                    type="incongruent",
                    cue=stimulus_dict["cue2"],
                    flankers=stimulus_dict["flankers_r"],
                    target=stimulus_dict["incongruent_rlr"],
                )
            )

    random.shuffle(all_trials)
    return all_trials
