import random
from collections import OrderedDict

from psychopy import core, event, logging

from classes.show_info import show_info
from classes.procedures.diamond_task.triggers import TriggerHandler, TriggerTypes, create_eeg_port
from classes.procedures.diamond_task.prepare_experiment import prepare_trials
from classes.procedures.diamond_task.load_data import load_stimuli


def diamond_task(
    win,
    screen_res,
    config,
    data_saver,
):
    clock = core.Clock()
    mouse = event.Mouse(win=win, visible=False)

    # load stimulus
    stimulus = load_stimuli(win=win, config=config, screen_res=screen_res)

    # EEG triggers
    if config["Send_EEG_trigg"]:
        port_eeg = create_eeg_port()
    else:
        port_eeg = None
    trigger_handler = TriggerHandler(port_eeg, data_saver=data_saver)

    for block in config["Experiment_blocks"]:
        trigger_handler.prepare_trigger(
            trigger_type=TriggerTypes.BLOCK_START,
            block_type=block["type"],
        )
        trigger_handler.send_trigger()
        logging.data(f"Entering block: {block}")
        logging.flush()

        if block["type"] == "break":
            show_info(
                win=win,
                file_name=block["file_name"],
                config=config,
                screen_width=screen_res["width"],
                data_saver=data_saver,
            )
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        for trial in block["trials"]:
            response_data = []

            # # ! show empty screen between trials
            # empty_screen_between_trials = random.uniform(*config["Empty_screen_between_trials"])
            # win.flip()
            # core.wait(empty_screen_between_trials)
            # data_saver.check_exit()













            # save beh
            # fmt: off
            cue_name = trial["cue"].text
            behavioral_data = OrderedDict(
                block_type=block["type"],
                trial_type=trial["type"],
                cue_name=cue_name,
                target_name=trial["target"].name,
                response=response,
                rt=reaction_time,
                reaction=reaction,
                threshold_rt=feedback_timer.thresholds[cue_name] if config["Show_feedback"] else None,
                empty_screen_between_trials=empty_screen_between_trials,
                cue_show_time=cue_show_time if config["Show_cues"] else None,
                empty_screen_after_cue_show_time=empty_screen_after_cue_show_time if config["Show_cues"] else None,
                fixation_show_time=fixation_show_time,
                flanker_show_time=flanker_show_time if "Flanker_show_time" in config else None,
                target_show_time=target_show_time,
                empty_screen_after_response_show_time=empty_screen_after_response_show_time,
                feedback_show_time=feedback_show_time if config["Show_feedback"] else None,
                feedback_type=feedback_type if config["Show_feedback"] else None,
            )
            # fmt: on
            data_saver.beh.append(behavioral_data)
            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.flush()
