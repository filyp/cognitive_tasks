import random

from psychopy import core, event, logging, visual

from classes.prepare_experiment import prepare_trials
from classes.show_info import show_info
from classes.triggers import TriggerTypes
from classes.feedback import FeedbackTimer


def show(
    win,
    screen_res,
    stimulus,
    config,
    data_saver,
    trigger_handler,
    frame_time=1 / 60.0,
):
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
                data_saver=data_saver,
            )
            continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, stimulus)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        if config["Show_feedback"]:
            # if we show cues, we need a separate cutoff for each of them
            feedback_timer = FeedbackTimer(
                config["Feedback_initial_cutoff"],
                timer_names=config["Cues"] if config["Show_cues"] else [""],
            )

        for trial in block["trials"]:
            reaction_time = None
            response = None

            if config["Show_cues"]:
                # it's a version of the experiment where we show cues before stimuli
                # ! draw cue
                cue_show_time = random.uniform(*config["Cue_show_time"])
                cue = trial["cue"]
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.CUE,
                    block_type=block["type"],
                    cue_name=trial["cue"].text,
                    target_name=trial["target"].name,
                )

                cue.setAutoDraw(True)
                win.flip()
                trigger_handler.send_trigger()

                core.wait(cue_show_time)
                cue.setAutoDraw(False)
                data_saver.check_exit()
                win.flip()

                # ! draw empty screen
                empty_screen_show_time = random.uniform(*config["Empty_screen_1_show_time"])
                clock.reset()
                while clock.getTime() < empty_screen_show_time:
                    data_saver.check_exit()
                    win.flip()

            # ! draw fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            core.wait(fixation_show_time)
            stimulus["fixation"].setAutoDraw(False)
            data_saver.check_exit()

            if "Flanker_show_time" in config:
                # it's a version of the experiment where we first draw flankers, then target
                # ! draw flankers
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.FLANKER,
                    block_type=block["type"],
                    cue_name=trial["cue"].text,
                    target_name=trial["target"].name,
                )
                flanker_show_time = random.uniform(*config["Flanker_show_time"])
                trial["flankers"].setAutoDraw(True)

                win.flip()
                trigger_handler.send_trigger()
                core.wait(flanker_show_time)
                trial["flankers"].setAutoDraw(False)

            # ! draw target
            # we assume no one will respond correctly during target
            # if someone clicks while target is displayed,
            # it will be registered as a click immediatly after target disappears
            trigger_handler.prepare_trigger(
                trigger_type=TriggerTypes.TARGET,
                block_type=block["type"],
                cue_name=trial["cue"].text,
                target_name=trial["target"].name,
            )
            target_show_time = random.uniform(*config["Target_show_time"])
            trial["target"].setAutoDraw(True)
            event.clearEvents()
            win.callOnFlip(clock.reset)
            win.callOnFlip(mouse.clickReset)

            win.flip()
            trigger_handler.send_trigger()
            while clock.getTime() < target_show_time:
                data_saver.check_exit()
                win.flip()
            trial["target"].setAutoDraw(False)
            win.flip()

            # ! draw empty screen and await response
            empty_screen_show_time = random.uniform(*config["Response_time_window"])
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
                    # logging.data(f"mouse_press_times={mouse_press_times}")
                    # logging.data(f"keys={keys}")

                    trigger_handler.prepare_trigger(
                        trigger_type=TriggerTypes.REACTION,
                        block_type=block["type"],
                        cue_name=trial["cue"].text,
                        target_name=trial["target"].name,
                        response=keys[0],
                    )
                    trigger_handler.send_trigger()
                    response = keys[0]
                    mouse.clickReset()
                    event.clearEvents()
                    logging.flush()
                    break  # if we hot a response, break out of this stage
                data_saver.check_exit()
                win.flip()

            if config["Use_whole_response_time_window"]:
                while clock.getTime() < target_show_time + empty_screen_show_time:
                    data_saver.check_exit()
                    win.flip()

            # ! show empty screen after response
            empty_show_time = random.uniform(*config["Empty_screen_after_response_show_time"])
            core.wait(empty_show_time)
            data_saver.check_exit()

            # check if reaction was correct
            if trial["target"].name in ["congruent_lll", "incongruent_rlr"]:
                # left is correct
                correct_key = config["Keys"][0]
            elif trial["target"].name in ["congruent_rrr", "incongruent_lrl"]:
                # right is correct
                correct_key = config["Keys"][1]

            if response == correct_key:
                reaction = "correct"
            else:
                reaction = "incorrect"

            # ! draw feedback
            if config["Show_feedback"]:
                feedback_timer.update_cutoff(
                    target_name=trial["target"].name,
                    reaction=reaction,
                    timer_name=trial["cue"].text,
                )
                feedback_show_time = random.uniform(*config["Feedback_show_time"])
                if reaction == "correct":
                    feedback_type, trigger_type = feedback_timer.get_feedback(
                        reaction_time=reaction_time,
                        timer_name=trial["cue"].text,
                    )
                    trigger_handler.prepare_trigger(
                        trigger_type=trigger_type,
                        block_type=block["type"],
                        cue_name=trial["cue"].text,
                        target_name=trial["target"].name,
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
            cue_name = trial["cue"].text
            behavioral_data = dict(
                block_type=block["type"],
                trial_type=trial["type"],
                cue_name=cue_name,
                target_name=trial["target"].name,
                response=response,
                rt=reaction_time,
                reaction=reaction,
                cutoff=feedback_timer.cutoffs[cue_name] if config["Show_feedback"] else None,
            )
            data_saver.beh.append(behavioral_data)
            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.flush()
