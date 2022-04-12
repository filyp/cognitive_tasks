import random

from psychopy import logging


def prepare_trials(block, stimulus):
    all_trials = []

    number_of_trials = block.get("number_of_trials", 0)  # if not given, assume it's a break block
    ratio_of_congruent = block.get("ratio_of_congruent", 0.5)
    ratio_of_first_cue = block.get("ratio_of_first_cue", 0)  # if not given, assume cues not needed

    number_of_congruent_trials = number_of_trials * ratio_of_congruent
    number_of_incongruent_trials = number_of_trials - number_of_congruent_trials

    num_of_congruent_first_cue = number_of_congruent_trials * ratio_of_first_cue
    num_of_congruent_second_cue = number_of_congruent_trials - num_of_congruent_first_cue
    num_of_incongruent_first_cue = number_of_incongruent_trials * ratio_of_first_cue
    num_of_incongruent_second_cue = number_of_incongruent_trials - num_of_incongruent_first_cue

    logging.data(
        f"""
    Preparing trials:
        block={block}
        num_of_congruent_first_cue={num_of_congruent_first_cue}
        num_of_congruent_second_cue={num_of_congruent_second_cue}
        num_of_incongruent_first_cue={num_of_incongruent_first_cue}
        num_of_incongruent_second_cue={num_of_incongruent_second_cue}
    """
    )

    assert num_of_congruent_first_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_congruent_first_cue // 2)):
        all_trials.append(
            dict(
                type="congruent",
                cue=stimulus["cue1"],
                flankers=stimulus["flankers_l"],
                target=stimulus["congruent_lll"],
                target_name="congruent_lll",
            )
        )
        all_trials.append(
            dict(
                type="congruent",
                cue=stimulus["cue1"],
                flankers=stimulus["flankers_r"],
                target=stimulus["congruent_rrr"],
                target_name="congruent_rrr",
            )
        )

    assert num_of_congruent_second_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_congruent_second_cue // 2)):
        all_trials.append(
            dict(
                type="congruent",
                cue=stimulus["cue2"],
                flankers=stimulus["flankers_l"],
                target=stimulus["congruent_lll"],
                target_name="congruent_lll",
            )
        )
        all_trials.append(
            dict(
                type="congruent",
                cue=stimulus["cue2"],
                flankers=stimulus["flankers_r"],
                target=stimulus["congruent_rrr"],
                target_name="congruent_rrr",
            )
        )

    assert num_of_incongruent_first_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_incongruent_first_cue // 2)):
        all_trials.append(
            dict(
                type="incongruent",
                cue=stimulus["cue1"],
                flankers=stimulus["flankers_l"],
                target=stimulus["incongruent_lrl"],
                target_name="incongruent_lrl",
            )
        )
        all_trials.append(
            dict(
                type="incongruent",
                cue=stimulus["cue1"],
                flankers=stimulus["flankers_r"],
                target=stimulus["incongruent_rlr"],
                target_name="incongruent_rlr",
            )
        )

    assert num_of_incongruent_second_cue % 2 == 0  # it must be even
    for _ in range(int(num_of_incongruent_second_cue // 2)):
        all_trials.append(
            dict(
                type="incongruent",
                cue=stimulus["cue2"],
                flankers=stimulus["flankers_l"],
                target=stimulus["incongruent_lrl"],
                target_name="incongruent_lrl",
            )
        )
        all_trials.append(
            dict(
                type="incongruent",
                cue=stimulus["cue2"],
                flankers=stimulus["flankers_r"],
                target=stimulus["incongruent_rlr"],
                target_name="incongruent_rlr",
            )
        )

    random.shuffle(all_trials)
    return all_trials
