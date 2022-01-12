import random
import time

from psychopy import core, event, visual

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
        win, color="black", text="+", height=2 * config["Fix_size"], pos=(0, 10)
    )
    clock = core.Clock()

    for block in config["Experiment_blocks"]:
        if block["type"] == "break":
            show_info(
                win=win,
                file_name=block["file_name"],
                text_size=config["Text_size"],
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

        for trial in block["trials"]:
            trigger_name = prepare_trigger_name(trial=trial, block_type=block["type"])
            reaction_time = None
            response = None
            acc = "negative"

            # draw fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            show_text(win, fixation, fixation_show_time, participant_info, beh, triggers_list)

            # draw target
            trigger_no, triggers_list = prepare_trigger(
                trigger_type=TriggerTypes.TARGET,
                trigger_no=trigger_no,
                triggers_list=triggers_list,
                trigger_name=trigger_name,
            )
            target_show_time = random.uniform(*config["Target_show_time"])
            trial["target"]["stimulus"].setAutoDraw(True)
            win.callOnFlip(clock.reset)
            event.clearEvents()
            win.flip()

            send_trigger(
                port_eeg=port_eeg,
                trigger_no=trigger_no,
                send_eeg_triggers=config["Send_EEG_trigg"],
            )

            while clock.getTime() < target_show_time:
                key = event.getKeys(keyList=config["Keys"])
                if key:
                    reaction_time = clock.getTime()
                    trigger_no, triggers_list = prepare_trigger(
                        trigger_type=TriggerTypes.RE,
                        trigger_no=trigger_no,
                        triggers_list=triggers_list,
                        trigger_name=trigger_name[:-1] + key[0],
                    )
                    send_trigger(
                        port_eeg=port_eeg,
                        trigger_no=trigger_no,
                        send_eeg_triggers=config["Send_EEG_trigg"],
                    )
                    response = key[0]
                    break

                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
                win.flip()
            # print (target_show_time-clock.getTime())*1000
            trial["target"]["stimulus"].setAutoDraw(False)
            win.flip()

            # empty screen
            empty_screen_show_time = random.uniform(*config["Empty_screen_show_time"])
            while clock.getTime() < empty_screen_show_time:
                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
                win.flip()
            # print (empty_screen_show_time-clock.getTime())*1000

            # save beh
            beh.append(
                {
                    "block type": block["type"],
                    "trial type": trial["type"],
                    "cue name": trial["cue"]["name"],
                    "target name": trial["target"]["name"],
                    "response": response,
                    "rt": reaction_time,
                    "reaction": True if acc == "positive" else False,
                }
            )

    return beh, triggers_list
