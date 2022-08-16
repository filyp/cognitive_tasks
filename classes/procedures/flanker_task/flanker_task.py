import random
from collections import OrderedDict

from psychopy import core, event, logging

from classes.show_info import show_info
from classes.procedures.flanker_task.load_data import load_stimuli
from classes.procedures.flanker_task.triggers import (
    TriggerHandler,
    TriggerTypes,
    create_eeg_port,
)
from classes.procedures.flanker_task.prepare_experiment import prepare_trials
from classes.procedures.flanker_task.feedback import (
    FeedbackTimerSteps,
    FeedbackTimerMovingMedian,
)


def check_response(config, event, mouse, clock, trigger_handler, block, trial, response_data):
    keylist = [key for group in config["Keys"] for key in group]
    keys = event.getKeys(keyList=keylist)
    _, mouse_press_times = mouse.getPressed(getTime=True)

    if mouse_press_times[0] != 0.0:
        keys.append("mouse_left")
    elif mouse_press_times[1] != 0.0:
        keys.append("mouse_middle")
    elif mouse_press_times[2] != 0.0:
        keys.append("mouse_right")

    if keys:
        reaction_time = clock.getTime()
        if response_data == []:
            trigger_type = TriggerTypes.REACTION
        else:
            trigger_type = TriggerTypes.SECOND_REACTION
        trigger_handler.prepare_trigger(
            trigger_type=trigger_type,
            block_type=block["type"],
            cue_name=trial["cue"].text,
            target_name=trial["target_name"],
            response=keys[0],
        )
        trigger_handler.send_trigger()
        response = keys[0]
        mouse.clickReset()
        event.clearEvents()
        return response, reaction_time
    else:
        return None


def get_reaction_stats(RTs_in_block, num_of_errors_in_block):
    if RTs_in_block is None or num_of_errors_in_block is None:
        return ""
    if RTs_in_block == []:
        return ""

    mean_rt = sum(RTs_in_block) / len(RTs_in_block)
    return f"Średni czas reakcji: {int(mean_rt * 1000)} ms\nLiczba błędów: {num_of_errors_in_block}"


def flanker_task(
    win,
    screen_res,
    config,
    data_saver,
):
    clock = core.Clock()
    mouse = event.Mouse(win=win, visible=False)

    RTs_in_block = None
    num_of_errors_in_block = None

    # load stimulus
    stimulus = load_stimuli(win=win, config=config, screen_res=screen_res)

    # EEG triggers
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
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
                insert=get_reaction_stats(RTs_in_block, num_of_errors_in_block),
            )
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        if config["Show_feedback"]:
            # if we show cues, we need a separate threshold RT for each of them
            # feedback_timer = FeedbackTimerSteps(
            feedback_timer = FeedbackTimerMovingMedian(
                config["Feedback_initial_threshold_rt"],
                timer_names=config["Cues"] if config["Show_cues"] else [""],
            )
        
        RTs_in_block = []
        num_of_errors_in_block = 0

        for trial in block["trials"]:
            response_data = []

            # ! show empty screen between trials
            empty_screen_between_trials = random.uniform(*config["Empty_screen_between_trials"])
            win.flip()
            core.wait(empty_screen_between_trials)
            data_saver.check_exit()

            if config["Show_cues"]:
                # it's a version of the experiment where we show cues before stimuli
                # ! draw cue
                cue_show_time = random.uniform(*config["Cue_show_time"])
                cue = trial["cue"]
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.CUE,
                    block_type=block["type"],
                    cue_name=trial["cue"].text,
                    target_name=trial["target_name"],
                )

                cue.setAutoDraw(True)
                win.flip()
                trigger_handler.send_trigger()

                core.wait(cue_show_time)
                cue.setAutoDraw(False)
                data_saver.check_exit()
                win.flip()

                # ! draw empty screen
                empty_screen_after_cue_show_time = random.uniform(
                    *config["Empty_screen_after_cue_show_time"]
                )
                clock.reset()
                while clock.getTime() < empty_screen_after_cue_show_time:
                    data_saver.check_exit()
                    win.flip()

            # ! draw fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            for fixation in stimulus["fixations"]:
                fixation.setAutoDraw(True)
            win.flip()
            core.wait(fixation_show_time)
            if not config.get("Keep_fixation_until_target"):
                for fixation in stimulus["fixations"]:
                    fixation.setAutoDraw(False)
            data_saver.check_exit()

            if "Flanker_show_time" in config:
                # it's a version of the experiment where we first draw flankers, then target
                # ! draw flankers
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.FLANKER,
                    block_type=block["type"],
                    cue_name=trial["cue"].text,
                    target_name=trial["target_name"],
                )
                flanker_show_time = random.uniform(*config["Flanker_show_time"])
                for flanker in trial["flankers"]:
                    flanker.setAutoDraw(True)

                win.flip()
                trigger_handler.send_trigger()
                core.wait(flanker_show_time)
                for flanker in trial["flankers"]:
                    flanker.setAutoDraw(False)

            if config.get("Keep_fixation_until_target"):
                for fixation in stimulus["fixations"]:
                    fixation.setAutoDraw(False)

            # ! draw target
            trigger_handler.prepare_trigger(
                trigger_type=TriggerTypes.TARGET,
                block_type=block["type"],
                cue_name=trial["cue"].text,
                target_name=trial["target_name"],
            )
            target_show_time = random.uniform(*config["Target_show_time"])
            for target in trial["target"]:
                target.setAutoDraw(True)
            event.clearEvents()
            win.callOnFlip(clock.reset)
            win.callOnFlip(mouse.clickReset)

            win.flip()
            trigger_handler.send_trigger()
            while clock.getTime() < target_show_time:
                res = check_response(
                    config,
                    event,
                    mouse,
                    clock,
                    trigger_handler,
                    block,
                    trial,
                    response_data,
                )
                if res is not None:
                    response_data.append(res)
                    break  # if we got a response, break out of this stage
                data_saver.check_exit()
                win.flip()
            for target in trial["target"]:
                target.setAutoDraw(False)
            win.flip()

            # ! draw empty screen and await response
            empty_screen_show_time = random.uniform(*config["Blank_screen_for_response_show_time"])
            if response_data == []:
                while clock.getTime() < target_show_time + empty_screen_show_time:
                    res = check_response(
                        config,
                        event,
                        mouse,
                        clock,
                        trigger_handler,
                        block,
                        trial,
                        response_data,
                    )
                    if res is not None:
                        response_data.append(res)
                        break  # if we got a response, break out of this stage
                    data_saver.check_exit()
                    win.flip()

            if config["Use_whole_response_time_window"]:
                # even if participant responded, wait out the response time window
                while clock.getTime() < target_show_time + empty_screen_show_time:
                    res = check_response(
                        config,
                        event,
                        mouse,
                        clock,
                        trigger_handler,
                        block,
                        trial,
                        response_data,
                    )
                    if res is not None:
                        response_data.append(res)
                    data_saver.check_exit()
                    win.flip()

            # ! show empty screen after response
            empty_screen_after_response_show_time = random.uniform(
                *config["Empty_screen_after_response_show_time"]
            )
            loop_start_time = clock.getTime()
            while clock.getTime() < loop_start_time + empty_screen_after_response_show_time:
                res = check_response(
                    config,
                    event,
                    mouse,
                    clock,
                    trigger_handler,
                    block,
                    trial,
                    response_data,
                )
                if res is not None:
                    response_data.append(res)
                data_saver.check_exit()
                win.flip()

            # check if reaction was correct
            if trial["target_name"] in ["congruent_lll", "incongruent_rlr"]:
                # left is correct
                correct_keys = config["Keys"][0]
            elif trial["target_name"] in ["congruent_rrr", "incongruent_lrl"]:
                # right is correct
                correct_keys = config["Keys"][1]

            response_keyname, reaction_time = response_data[0] if response_data != [] else (None, None)
            if response_keyname in correct_keys:
                reaction = "correct"
            else:
                reaction = "incorrect"
            if response_keyname in config["Keys"][0]:
                response_side = "l"
            elif response_keyname in config["Keys"][1]:
                response_side = "r"

            # ! draw feedback
            if config["Show_feedback"]:
                feedback_timer.update_threshold(
                    target_name=trial["target_name"],
                    reaction=reaction,
                    timer_name=trial["cue"].text,
                )
                feedback_show_time = random.uniform(*config["Feedback_show_time"])
                feedback_type = None
                if reaction == "correct":
                    feedback_type, trigger_type = feedback_timer.get_feedback(
                        reaction_time=reaction_time,
                        timer_name=trial["cue"].text,
                    )
                    trigger_handler.prepare_trigger(
                        trigger_type=trigger_type,
                        block_type=block["type"],
                        cue_name=trial["cue"].text,
                        target_name=trial["target_name"],
                    )
                    stimulus[feedback_type].setAutoDraw(True)

                    win.flip()
                    trigger_handler.send_trigger()
                    core.wait(feedback_show_time)
                    stimulus[feedback_type].setAutoDraw(False)
                    data_saver.check_exit()
                else:
                    core.wait(feedback_show_time)
                    data_saver.check_exit()

            # save beh
            # fmt: off
            cue_name = trial["cue"].text
            behavioral_data = OrderedDict(
                block_type=block["type"],
                trial_type=trial["type"],
                cue_name=cue_name,
                target_name=trial["target_name"],
                response=response_side,
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

            # update block stats
            if reaction_time is not None:
                RTs_in_block.append(reaction_time)
            num_of_errors_in_block += 1 if reaction == "incorrect" else 0

            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.flush()
