import random
from collections import OrderedDict

from psychopy import core, event, logging

from classes.show_info import show_info
from classes.procedures.monetary_incentive_delay.load_data import load_stimuli
from classes.procedures.monetary_incentive_delay.prepare_experiment import prepare_trials
from classes.procedures.monetary_incentive_delay.triggers import (
    TriggerHandler,
    TriggerTypes,
)
from classes.triggers_common import create_eeg_port

def monetary_incentive_delay(
    win,
    screen_res,
    config,
    data_saver,
):
    clock = core.Clock()

    target_show_time = config["Target_initial_show_time"]
    score = None

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
                insert=str(score),
            )
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        score = 0
        for trial in block["trials"]:
            beh = OrderedDict(
                block_type=block["type"],
                cue_type=trial["cue"].name,
                target_show_time=round(target_show_time, 3),
                fast_enough=None,
                reaction_time=None,
                waiting_for_reaction_timed_out=False,
                reacted_too_soon=False,
                target_anticipation_time=None,
                premature_reaction_time_since_cue_offset=None,
                feedback_type=None
            )

            # ! show empty screen between trials
            empty_screen_between_trials = random.uniform(*config["Empty_screen_between_trials"])
            core.wait(empty_screen_between_trials)
            data_saver.check_exit()

            # ! draw fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            core.wait(fixation_show_time)
            stimulus["fixation"].setAutoDraw(False)
            data_saver.check_exit()

            # ! draw cue
            event.clearEvents()
            cue_show_time = random.uniform(*config["Cue_show_time"])
            cue = trial["cue"]
            trigger_handler.prepare_trigger(
                trigger_type=TriggerTypes.CUE,
                block_type=block["type"],
                cue_name=cue.name.split("_")[1],
            )
            cue.setAutoDraw(True)
            # stimulus["circle"].setAutoDraw(True)
            win.flip()
            trigger_handler.send_trigger()
            win.callOnFlip(clock.reset)
            win.flip()
            while clock.getTime() < cue_show_time:
                keys = event.getKeys(keyList=config["Keys"])
                if keys:
                    beh["reacted_too_soon"] = True
                    trigger_handler.prepare_trigger(
                        trigger_type=TriggerTypes.PREMATURE_EARLY_REACTION,
                        block_type=block["type"],
                        cue_name=cue.name.split("_")[1],
                    )
                    trigger_handler.send_trigger()
                    break  # if we got a response, break out of this stage
                win.flip()
                data_saver.check_exit()
            cue.setAutoDraw(False)
            # stimulus["circle"].setAutoDraw(False)
            data_saver.check_exit()
            win.flip()

            # ! target anticipation
            if not beh["reacted_too_soon"]:
                blank_screen_time = random.uniform(*config["Target_anticipation_time"])
                beh["target_anticipation_time"] = blank_screen_time
                win.callOnFlip(clock.reset)
                win.flip()
                while clock.getTime() < blank_screen_time:
                    keys = event.getKeys(keyList=config["Keys"])
                    if keys:
                        rt = clock.getTime()
                        if rt < config["RT_after_cue_offset_cutting_off_reactions_on_cue"]:
                            trigger_type = TriggerTypes.PREMATURE_EARLY_REACTION
                        else:
                            trigger_type = TriggerTypes.PREMATURE_LATE_REACTION
                        trigger_handler.prepare_trigger(
                            trigger_type=trigger_type,
                            block_type=block["type"],
                            cue_name=cue.name.split("_")[1],
                        )
                        trigger_handler.send_trigger()
                        beh["reacted_too_soon"] = True
                        beh["premature_reaction_time_since_cue_offset"] = rt
                        break  # if we got a response, break out of this stage
                    win.flip()
                    data_saver.check_exit()

            # ! draw target
            if not beh["reacted_too_soon"]:
                # there was no premature reaction
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.TARGET,
                    block_type=block["type"],
                    cue_name=cue.name.split("_")[1],
                )
                stimulus["target"].setAutoDraw(True)
                win.callOnFlip(clock.reset)
                win.flip()
                trigger_handler.send_trigger()

                while clock.getTime() < target_show_time:
                    keys = event.getKeys(keyList=config["Keys"])
                    if keys:
                        beh["reaction_time"] = clock.getTime()
                        beh["fast_enough"] = True
                        trigger_handler.prepare_trigger(
                            trigger_type=TriggerTypes.REACTION,
                            block_type=block["type"],
                            cue_name=cue.name.split("_")[1],
                        )
                        trigger_handler.send_trigger()
                        break  # if we got a response, break out of this stage
                    win.flip()
                    data_saver.check_exit()
                stimulus["target"].setAutoDraw(False)
                win.flip()

            # ! wait after target for reaction
            if beh["reaction_time"] is None and not beh["reacted_too_soon"]:
                while clock.getTime() < config["Response_timeout"]:
                    keys = event.getKeys(keyList=config["Keys"])
                    if keys:
                        beh["reaction_time"] = clock.getTime()
                        beh["fast_enough"] = False
                        trigger_handler.prepare_trigger(
                            trigger_type=TriggerTypes.REACTION,
                            block_type=block["type"],
                            cue_name=cue.name.split("_")[1],
                        )
                        trigger_handler.send_trigger()
                        break  # if we got a response, break out of this stage
                    win.flip()
                    data_saver.check_exit()
                    
                if beh["reaction_time"] is None:
                    beh["waiting_for_reaction_timed_out"] = True

            # ! update target show time
            if trial["cue"].name == "cue_incentive":
                # update only in the incentivised trials
                if beh["fast_enough"]:
                    # shorten the time, only if the target has hit
                    target_show_time -= 0.010
                    # ! update score
                    score += 1
                else:
                    target_show_time += 0.010
                    # ! update score
                    score -= 1

            # ! blank screen between response and feedback
            blank_screen_time = random.uniform(
                *config["Empty_screen_between_response_and_feedback"]
            )
            core.wait(blank_screen_time)
            data_saver.check_exit()

            # ! draw feedback
            feedback_show_time = random.uniform(*config["Feedback_show_time"])
            if trial["cue"].name == "cue_incentive":
                if beh["fast_enough"]:
                    beh["feedback_type"] = "feedback_good"
                    trigger_type = TriggerTypes.FEEDBACK_GOOD
                else:
                    beh["feedback_type"] = "feedback_bad"
                    trigger_type = TriggerTypes.FEEDBACK_BAD
            elif trial["cue"].name == "cue_neutral":
                beh["feedback_type"] = "feedback_neutral"
                trigger_type = TriggerTypes.FEEDBACK_NEUTRAL

            stimulus[beh["feedback_type"]].setAutoDraw(True)
            # if trial["cue"].name == "cue_neutral":
            #     stimulus["circle"].setAutoDraw(True)
            trigger_handler.prepare_trigger(
                trigger_type=trigger_type,
                block_type=block["type"],
                cue_name=cue.name.split("_")[1],
            )
            win.flip()
            trigger_handler.send_trigger()
            core.wait(feedback_show_time)
            stimulus[beh["feedback_type"]].setAutoDraw(False)
            # if trial["cue"].name == "cue_neutral":
            #     stimulus["circle"].setAutoDraw(False)
            win.flip()

            # save beh
            data_saver.beh.append(beh)
            logging.data(f"Behavioral data: {beh}\n")
            logging.flush()
