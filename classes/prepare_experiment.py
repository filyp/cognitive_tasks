import random

from psychopy import logging


def prepare_trials_type(stimulus_pairs, number_of_trials):
    trials = []
    for idx in range(number_of_trials):
        trial_type = idx % len(stimulus_pairs)
        trials.append(stimulus_pairs[trial_type])
    return trials


def prepare_stimulus_pairs(cue_name, target_name, stim_name, stimulus):
    stimulus_pairs = []
    idx = 1
    while True:
        cue = [stim for stim in stimulus if stim["name"].startswith("{}_{}".format(idx, cue_name))]
        target = [
            stim for stim in stimulus if stim["name"].startswith("{}_{}".format(idx, target_name))
        ]
        if cue and target:
            pair = {"type": stim_name, "cue": cue[0], "target": target[0]}
            stimulus_pairs.append(pair)
            idx += 1
        else:
            return stimulus_pairs


def prepare_trials(block, stimulus):
    logging.data(f"{block=}")
    logging.data(f"{stimulus=}")
    logging.flush()

    all_trials = []

    if "number_of_shape_trials" in block:

        stimulus_pairs = prepare_stimulus_pairs(
            cue_name="neutral",
            target_name="color_1",
            stim_name="shape",
            stimulus=stimulus,
        )

        for idx in range(len(stimulus_pairs)):
            target_name = stimulus_pairs[idx]["target"]["name"]
            new_target_idx = (int(target_name.split("_")[0]) % len(stimulus_pairs)) + 1
            new_target_name = "{}_{}".format(new_target_idx, target_name.split("_", 1)[1])
            stimulus_pairs[idx]["target"] = [
                stim for stim in stimulus if stim["name"] == new_target_name
            ][0]

        trials = prepare_trials_type(
            stimulus_pairs=stimulus_pairs,
            number_of_trials=block["number_of_shape_trials"],
        )
        all_trials += trials

    if "number_of_go_trials" in block:
        stimulus_pairs = prepare_stimulus_pairs(
            cue_name="neutral", target_name="color_1", stim_name="go", stimulus=stimulus
        )
        trials = prepare_trials_type(
            stimulus_pairs=stimulus_pairs, number_of_trials=block["number_of_go_trials"]
        )
        all_trials += trials

    if "number_of_color_trials" in block:
        stimulus_pairs = prepare_stimulus_pairs(
            cue_name="neutral",
            target_name="color_2",
            stim_name="color",
            stimulus=stimulus,
        )
        trials = prepare_trials_type(
            stimulus_pairs=stimulus_pairs,
            number_of_trials=block["number_of_color_trials"],
        )
        all_trials += trials

    random.shuffle(all_trials)
    return all_trials
