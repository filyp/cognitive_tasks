import random
import time
from cmath import log

from psychopy import core, event, logging, visual

from classes.check_exit import check_exit
from classes.prepare_experiment import prepare_trials
from classes.show_info import show_info, show_text
from classes.triggers import (
    TriggerTypes,
    prepare_trigger,
    prepare_trigger_name,
    send_trigger,
)


def show(
    win,
    screen_res,
    stimulus,
    config,
    participant_info,
    port_eeg,
    trigger_no,
    triggers_list,
    frame_time=1 / 60.0,
):
    beh = []
    fixation = visual.TextStim(
        win, color=config["Text_color"], text="+", height=2 * config["Fixation_size"], pos=(0, 0)
    )
    clock = core.Clock()
    mouse = event.Mouse(win=win, visible=False)

    for block in config["Experiment_blocks"]:
        logging.data(f"Entering block: {block}")
        logging.flush()

        if block["type"] == "break":
            show_info(
                win=win,
                file_name=block["file_name"],
                text_size=config["Text_size"],
                text_color=config["Text_color"],
                screen_width=screen_res["width"],
                participant_info=participant_info,
                beh=beh,
                triggers_list=triggers_list,
            )
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        # logging.data(f"trials: {block['trials']}")
        # logging.flush()

        for trial in block["trials"]:
            trigger_name = prepare_trigger_name(trial=trial, block_type=block["type"])
            reaction_time = None
            response = None

            if config["Cues"] is not None:
                # it's a version of the experiment where we show cues before stimuli
                # ! draw cue
                cue_show_time = random.uniform(*config["Cue_show_time"])
                cue = trial["cue"]["stimulus"]
                show_text(win, cue, cue_show_time, participant_info, beh, triggers_list)

                # ! draw empty screen
                empty_screen_show_time = random.uniform(*config["Empty_screen_1_show_time"])
                clock.reset()
                while clock.getTime() < empty_screen_show_time:
                    check_exit(
                        participant_info=participant_info, beh=beh, triggers_list=triggers_list
                    )
                    win.flip()

            # ! draw fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            show_text(win, fixation, fixation_show_time, participant_info, beh, triggers_list)

            # ! draw target
            trigger_no, triggers_list = prepare_trigger(
                trigger_type=TriggerTypes.TARGET,
                trigger_no=trigger_no,
                triggers_list=triggers_list,
                trigger_name=trigger_name,
            )
            target_show_time = random.uniform(*config["Target_show_time"])
            trial["target"]["stimulus"].setAutoDraw(True)
            win.callOnFlip(clock.reset)
            win.callOnFlip(mouse.clickReset)
            event.clearEvents()
            win.flip()

            send_trigger(
                port_eeg=port_eeg,
                trigger_no=trigger_no,
                send_eeg_triggers=config["Send_EEG_trigg"],
            )

            while clock.getTime() < target_show_time:
                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
                win.flip()
            # print (target_show_time-clock.getTime())*1000
            trial["target"]["stimulus"].setAutoDraw(False)
            win.flip()

            # ! draw empty screen
            empty_screen_show_time = random.uniform(*config["Empty_screen_2_show_time"])
            while clock.getTime() < target_show_time + empty_screen_show_time:
                keys = event.getKeys(keyList=config["Keys"])
                _, mouse_press_times = mouse.getPressed(getTime=True)

                if mouse_press_times[0] != 0.0:
                    keys.append("mouse_left")
                elif mouse_press_times[1] != 0.0:
                    keys.append("mouse_middle")
                elif mouse_press_times[2] != 0.0:
                    keys.append("mouse_right")

                if keys:
                    reaction_time = clock.getTime()
                    logging.data(f"{mouse_press_times=}")
                    logging.data(f"{keys=}")

                    trigger_no, triggers_list = prepare_trigger(
                        trigger_type=TriggerTypes.RE,
                        trigger_no=trigger_no,
                        triggers_list=triggers_list,
                        trigger_name=trigger_name[:-1] + keys[0],
                    )
                    send_trigger(
                        port_eeg=port_eeg,
                        trigger_no=trigger_no,
                        send_eeg_triggers=config["Send_EEG_trigg"],
                    )
                    response = keys[0]
                    mouse.clickReset()
                    event.clearEvents()
                    logging.flush()

                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
                win.flip()

            # check if reaction was correct
            if trial["target"]["name"] in ["congruent_lll", "incongruent_rlr"]:
                # left is correct
                correct_key = config["Keys"][0]
            elif trial["target"]["name"] in ["congruent_rrr", "incongruent_lrl"]:
                # right is correct
                correct_key = config["Keys"][1]

            if response == correct_key:
                reaction = "correct"
            else:
                reaction = "incorrect"

            # save beh
            behavioral_data = {
                "block type": block["type"],
                "trial type": trial["type"],
                "cue name": trial["cue"]["name"] if config["Cues"] is not None else None,
                "target name": trial["target"]["name"],
                "response": response,
                "rt": reaction_time,
                "reaction": reaction,
            }
            beh.append(behavioral_data)
            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.flush()

    return beh, triggers_list
