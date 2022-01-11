from psychopy import visual, event, core
import random
import time

from classes.check_exit import check_exit
from classes.show_info import show_info, show_text
from classes.triggers import (
    prepare_trigger,
    TriggerTypes,
    prepare_trigger_name,
    send_trigger,
)


def show(
    win,
    screen_res,
    experiment,
    config,
    participant_info,
    port_eeg,
    trigger_no,
    triggers_list,
    frame_time=1 / 60.0,
):
    beh = []
    rt_sum = 0
    rt_mean = 0
    fixation = visual.TextStim(
        win, color="black", text="+", height=2 * config["Fix_size"], pos=(0, 10)
    )
    clock = core.Clock()

    for block in experiment:

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
            show_text(win, fixation, fixation_show_time, participant_info, beh, triggers_list)

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
                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
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

                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
                win.flip()
            # print (target_show_time-clock.getTime())*1000
            trial["target"]["stimulus"].setAutoDraw(False)
            win.flip()

            # empty screen
            empty_screen_show_time = random.uniform(
                config["Empty_screen_show_time"][0], config["Empty_screen_show_time"][1]
            )
            while clock.getTime() < empty_screen_show_time:
                check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
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
                feedback_type = "Feedback_{}_{}_".format(trial["type"], acc)

                # draw feedback
                if config[feedback_type + "show"]:
                    feedback_text = config[feedback_type + "text"]
                    feedback_text = visual.TextStim(
                        win,
                        color="black",
                        text=feedback_text,
                        height=config["Feedback_size"],
                    )
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
                    feedback_text.setAutoDraw(True)
                    win.flip()
                    send_trigger(
                        port_eeg=port_eeg,
                        trigger_no=trigger_no,
                        send_eeg_triggers=config["Send_EEG_trigg"],
                    )
                    time.sleep(feedback_show_time - frame_time)
                    feedback_text.setAutoDraw(False)
                    check_exit(part_id=participant_info, beh=beh, triggers_list=triggers_list)
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
