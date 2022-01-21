import random

from psychopy import logging


def prepare_trials(block, stimulus):
    # logging.data(f"{block=}")
    # logging.data(f"{stimulus=}")
    # logging.flush()

    all_trials = []

    stimulus_dict = {stim["name"]: stim for stim in stimulus}

    number_of_trials = block.get("number_of_trials", 0)  # if not given, assume it's a break block
    ratio_of_congruent = block.get("ratio_of_congruent", 0.5)
    ratio_of_first_cue = block.get("ratio_of_first_cue", 0.5)

    number_of_congruent_trials = number_of_trials * ratio_of_congruent
    number_of_incongruent_trials = number_of_trials - number_of_congruent_trials

    num_of_congruent_first_cue = number_of_congruent_trials * ratio_of_first_cue
    num_of_congruent_second_cue = number_of_congruent_trials - num_of_congruent_first_cue
    num_of_incongruent_first_cue = number_of_incongruent_trials * ratio_of_first_cue
    num_of_incongruent_second_cue = number_of_incongruent_trials - num_of_incongruent_first_cue

    logging.data(
        f"""
    Preparing trials:
        {block=}
        {num_of_congruent_first_cue=}
        {num_of_congruent_second_cue=}
        {num_of_incongruent_first_cue=}
        {num_of_incongruent_second_cue=}
    """
    )

    assert num_of_congruent_first_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_congruent_first_cue // 2)):
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

    assert num_of_congruent_second_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_congruent_second_cue // 2)):
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

    assert num_of_incongruent_first_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_incongruent_first_cue // 2)):
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

    assert num_of_incongruent_second_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_incongruent_second_cue // 2)):
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
