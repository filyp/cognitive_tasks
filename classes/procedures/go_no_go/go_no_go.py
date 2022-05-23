import os
import random
import time

from psychopy import core, event, visual

from classes.show_info import show_info
from classes.procedures.go_no_go.load_data import load_data
from classes.procedures.go_no_go.prepare_experiment import prepare_trials
from classes.procedures.go_no_go.triggers import TriggerTypes, prepare_trigger, prepare_trigger_name, send_trigger, create_eeg_port


def go_no_go(
    win,
    screen_res,
    config,
    data_saver,
    frame_time=1 / 60.0,

):
    # load stimulus
    stimulus = load_data(win=win, folder_name=os.path.join("input_data", "go_no_go"), config=config, screen_res=screen_res)
    stimulus_dict = {stim["name"]: stim for stim in stimulus}

    # EEG triggers
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    triggers_list = list()
    trigger_no = 0

    beh = []
    rt_sum = 0
    rt_mean = 0
    fixation = visual.TextStim(
        win, color="black", text="+", height=2 * config["Fix_size"], pos=(0, 0.005)
    )
    clock = core.Clock()

    for block in config["Experiment_blocks"]:
        if block["type"] == "break":
            show_info(
                win=win,
                file_name=block["file_name"],
                config=config,
                screen_width=screen_res["width"],
                data_saver=data_saver,
            )
            continue
        elif block["type"] in ["calibration", "experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        if block["type"] == "calibration":
            rt_mean = 0
            rt_sum = 0

        for trial in block["trials"]:
            trigger_name = prepare_trigger_name(trial=trial, block_type=block["type"])
            reaction_time = None
            response = None
            acc = "negative"

            # draw fixation
            fixation_show_time = random.uniform(
                config["Fixation_show_time"][0], config["Fixation_show_time"][1]
            )
            fixation.setAutoDraw(True)
            win.flip()
            time.sleep(fixation_show_time)
            fixation.setAutoDraw(False)
            data_saver.check_exit()
            win.flip()


            # draw cue
            trigger_no, triggers_list = prepare_trigger(
                trigger_type=TriggerTypes.CUE,
                trigger_no=trigger_no,
                triggers_list=triggers_list,
                trigger_name=trigger_name,
            )
            cue_show_time = random.uniform(config["Cue_show_time"][0], config["Cue_show_time"][1])
            trial["cue"]["stimulus"].setAutoDraw(True)
            win.callOnFlip(clock.reset)
            event.clearEvents()
            win.flip()

            send_trigger(
                port_eeg=port_eeg,
                trigger_no=trigger_no,
                send_eeg_triggers=config["Send_EEG_trigg"],
            )

            while clock.getTime() < cue_show_time:
                data_saver.check_exit()
                win.flip()
            # print (cue_show_time - clock.getTime())*1000
            trial["cue"]["stimulus"].setAutoDraw(False)
            win.flip()

            # draw target
            trigger_no, triggers_list = prepare_trigger(
                trigger_type=TriggerTypes.TARGET,
                trigger_no=trigger_no,
                triggers_list=triggers_list,
                trigger_name=trigger_name,
            )
            target_show_time = random.uniform(
                config["Target_show_time"][0], config["Target_show_time"][1]
            )
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

                data_saver.check_exit()
                win.flip()
            # print (target_show_time-clock.getTime())*1000
            trial["target"]["stimulus"].setAutoDraw(False)
            win.flip()

            # empty screen
            empty_screen_show_time = random.uniform(
                config["Empty_screen_show_time"][0], config["Empty_screen_show_time"][1]
            )
            # ! NOTE THAT THE TIME EMPTY SCREEN IS SHOWN IS DECREASED BY THE TIME THE TARGET WAS SHOWN
            # ! THIS BUG IS KEPT IN ON PURPOSE, TO HAVE ALL THE COLLECTED DATA USE ONE PROCEDURE
            while clock.getTime() < empty_screen_show_time:
                data_saver.check_exit()
                win.flip()
            # print (empty_screen_show_time-clock.getTime())*1000

            # verify reaction
            if response and trial["type"] == "go":
                if not (
                    block["type"] == "experiment"
                    and reaction_time > rt_mean - rt_mean * block["cutoff"]
                ):
                    acc = "positive"
            elif not response and trial["type"] != "go":
                acc = "positive"

            # calibration
            if (
                block["type"] == "calibration"
                and trial["type"] == "go"
                and reaction_time is not None
            ):
                rt_sum += reaction_time

            # feedback
            if block["type"] == "experiment":
                # choose feedback type
                feedback_type = "Feedback_{}_{}".format(trial["type"], acc)

                # draw feedback
                if config[feedback_type + "_show"]:
                    feedback_name = config[feedback_type]
                    feedback = stimulus_dict[feedback_name]["stimulus"]
                    feedback_show_time = random.uniform(
                        config["Feedback_show_time"][0], config["Feedback_show_time"][1]
                    )
                    if acc == "positive":
                        trigger_type = TriggerTypes.FEEDB_GOOD
                    else:
                        trigger_type = TriggerTypes.FEEDB_BAD

                    trigger_no, triggers_list = prepare_trigger(
                        trigger_type=trigger_type,
                        trigger_no=trigger_no,
                        triggers_list=triggers_list,
                        trigger_name=trigger_name,
                    )
                    feedback.setAutoDraw(True)
                    win.flip()
                    send_trigger(
                        port_eeg=port_eeg,
                        trigger_no=trigger_no,
                        send_eeg_triggers=config["Send_EEG_trigg"],
                    )
                    time.sleep(feedback_show_time - frame_time)
                    feedback.setAutoDraw(False)
                    data_saver.check_exit()
                    win.flip()

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
                    "cal mean rt": rt_mean,
                    "cutoff": block["cutoff"] if block["type"] == "experiment" else None,
                }
            )

        if block["type"] == "calibration":
            rt_mean = rt_sum / len([trial for trial in block["trials"] if trial["type"] == "go"])

    return beh, triggers_list
