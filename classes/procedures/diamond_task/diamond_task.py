import random
from collections import OrderedDict

import numpy as np
from psychopy import core, event, logging, visual
from psychopy.hardware import joystick, keyboard

from classes.show_info import show_info
from classes.procedures.diamond_task.triggers import (
    TriggerHandler,
    TriggerTypes,
    create_eeg_port,
)
from classes.procedures.diamond_task.prepare_experiment import prepare_trials
from classes.procedures.diamond_task.load_data import load_stimuli


trait_names = ["rozmiar", "przejrzystość", "kształt", "kolor", "blask", "proporcje"]


def get_joystick_input(joy):
    x = joy.getX()
    y = joy.getY()
    responses = []
    if x == -1:
        responses.append("left")
    elif x == 1:
        responses.append("right")
    if y == 1:  # y axis is inverted
        responses.append("down")
    elif y == -1:
        responses.append("up")
    return responses


def wait_for_no_keys_pressed(win, joy=None, keyboard_=None):
    # make sure joystick or keyboard is unpressed
    # it also removes the finished keypresses from the buffer
    while get_keypresses(joy, keyboard_) != []:
        win.flip()


def get_keypresses(joy=None, keyboard=None):
    if joy is None:
        keys = keyboard.getKeys(keyList=["down", "left", "right"], waitRelease=False, clear=False)
        for key in keys:
            if key.duration is not None:
                # it means that some key was unpressed, so remove keypresses from buffer
                keyboard.clearEvents()
        return keys
    else:
        # joystick is connected, so use it instead of keyboard
        return get_joystick_input(joy)


def get_value_from_slider(
    slider, text, win, data_saver, stimulus, speed=1, joy=None, keyboard=None
):
    slider.markerPos = 50
    slider.setAutoDraw(True)
    stimulus["top_text"].setAutoDraw(True)
    stimulus["top_text"].text = text
    win.flip()

    while True:
        pressed = get_keypresses(joy, keyboard)
        if "left" in pressed:
            slider.markerPos -= speed
        if "right" in pressed:
            slider.markerPos += speed
        if "down" in pressed:
            break
        win.flip()
        data_saver.check_exit()
    while "down" in get_keypresses(joy, keyboard):
        win.flip()

    slider.setAutoDraw(False)
    stimulus["top_text"].setAutoDraw(False)
    win.flip()
    return slider.markerPos


def diamond_task(
    win,
    screen_res,
    config,
    data_saver,
):
    if config["Keys"] == "joystick":
        if joystick.getNumJoysticks() == 0:
            raise RuntimeError(
                "No joystick found. On linux you need to run this command first: modprobe joydev"
            )
        joy = joystick.Joystick(0)
        keyboard_ = None
    else:
        joy = None
        keyboard_ = keyboard.Keyboard()

    total_decision_clock = core.Clock()
    cue_decision_clock = core.Clock()

    # load stimulus
    stimulus = load_stimuli(win=win, config=config, screen_res=screen_res)

    slider_params = dict(
        win=win,
        size=(0.5, 0.03),
        ticks=[0, 100],
        borderColor=config["Text_color"],
        markerColor=config["Text_color"],
    )
    slider_arousal = visual.Slider(name="arousal", **slider_params)
    slider_valence = visual.Slider(name="valence", **slider_params)
    slider_confidence = visual.Slider(name="confidence", **slider_params)

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
            block["trials"] = prepare_trials(block, config, win)
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        for trial in block["trials"]:
            behavioral_data = OrderedDict(
                block_type=block["type"],
                choice=None,
                choice_correct=None,
                arousal=None,
                valence=None,
                confidence=None,
                total_decision_time=None,
                choice_prompt_decision_time=None,
                cue1_decision_time=None,
                cue2_decision_time=None,
                cue3_decision_time=None,
                cue4_decision_time=None,
                cue5_decision_time=None,
                cue6_decision_time=None,
                cues_taken=None,
                image=None,
                empty_screen_between_trials_time=None,
            )

            # ! show empty screen between trials
            min_time, max_time, step = config["Empty_screen_between_trials"]
            possible_times = np.arange(min_time, max_time + step, step)
            empty_screen_between_trials = random.choice(possible_times)
            win.flip()
            core.wait(empty_screen_between_trials)
            data_saver.check_exit()
            behavioral_data["empty_screen_between_trials_time"] = empty_screen_between_trials

            # ! show fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            core.wait(fixation_show_time)
            stimulus["fixation"].setAutoDraw(False)
            win.flip()
            data_saver.check_exit()

            if config["Show_images"]:
                # ! show image
                behavioral_data["image"] = trial["image"].name
                photo_show_time = random.uniform(*config["Photo_show_time"])
                trial["image"].setAutoDraw(True)
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.IMAGE,
                    block_type=block["type"],
                )
                win.flip()
                trigger_handler.send_trigger()
                core.wait(photo_show_time)
                trial["image"].setAutoDraw(False)
                win.flip()
                data_saver.check_exit()

            if config["Rate_arousal"]:
                # ! rate arousal
                behavioral_data["arousal"] = get_value_from_slider(
                    slider_arousal,
                    "Pobudzenie",
                    win,
                    data_saver,
                    stimulus,
                    config["Slider_speed"],
                    joy,
                    keyboard_,
                )

            if config["Rate_valence"]:
                # ! rate valence
                behavioral_data["valence"] = get_value_from_slider(
                    slider_valence,
                    "Nastrój",
                    win,
                    data_saver,
                    stimulus,
                    config["Slider_speed"],
                    joy,
                    keyboard_,
                )

            # ! show choice prompt
            stimulus["left_square"].setAutoDraw(True)
            stimulus["right_square"].setAutoDraw(True)
            stimulus["middle_text"].setAutoDraw(True)
            stimulus["left_text"].setAutoDraw(True)
            stimulus["right_text"].setAutoDraw(True)
            stimulus["middle_text"].text = ""
            stimulus["left_text"].text = "A"
            stimulus["right_text"].text = "B"
            stimulus["right_arrow"].setAutoDraw(True)
            stimulus["left_arrow"].setAutoDraw(True)
            stimulus["down_arrow"].setAutoDraw(True)
            win.callOnFlip(total_decision_clock.reset)
            win.callOnFlip(cue_decision_clock.reset)
            trigger_handler.prepare_trigger(
                trigger_type=TriggerTypes.CHOICE_PROMPT,
                block_type=block["type"],
            )
            win.flip()
            trigger_handler.send_trigger()

            # ! wait for response
            while True:
                keys = get_keypresses(joy, keyboard_)
                if keys:
                    behavioral_data["choice_prompt_decision_time"] = cue_decision_clock.getTime()
                    break
                data_saver.check_exit()
                win.flip()
            if "left" in keys:
                behavioral_data["choice"] = "A"
            if "right" in keys:
                behavioral_data["choice"] = "B"
            wait_for_no_keys_pressed(win, joy, keyboard_)

            cues_taken = 1
            num_of_cues = len(trait_names)
            for i, trait_name, info_pair in zip(
                range(num_of_cues), trait_names, trial["diamond_data"]
            ):
                if behavioral_data["choice"] is not None:
                    break

                # ! cue display
                stimulus["right_arrow"].setAutoDraw(False)
                stimulus["left_arrow"].setAutoDraw(False)
                stimulus["down_arrow"].setAutoDraw(False)
                stimulus["left_square"].setAutoDraw(True)
                stimulus["right_square"].setAutoDraw(True)
                stimulus["middle_text"].setAutoDraw(True)
                stimulus["left_text"].setAutoDraw(True)
                stimulus["right_text"].setAutoDraw(True)
                stimulus["middle_text"].text = trait_name
                stimulus["left_text"].text = info_pair[0]
                stimulus["right_text"].text = info_pair[1]
                win.callOnFlip(cue_decision_clock.reset)
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.CUES[i],
                    block_type=block["type"],
                )
                win.flip()
                trigger_handler.send_trigger()

                info_show_time = random.uniform(*config["Diamond_info_show_time"])
                core.wait(info_show_time)
                data_saver.check_exit()

                # ! cue prompt
                stimulus["right_arrow"].setAutoDraw(True)
                stimulus["left_arrow"].setAutoDraw(True)
                stimulus["down_arrow"].setAutoDraw(True)
                stimulus["left_square"].setAutoDraw(False)
                stimulus["right_square"].setAutoDraw(False)
                stimulus["middle_text"].setAutoDraw(False)
                stimulus["left_text"].setAutoDraw(False)
                stimulus["right_text"].setAutoDraw(False)
                if i == num_of_cues - 1:
                    stimulus["down_arrow"].setAutoDraw(False)
                win.flip()
                wait_for_no_keys_pressed(win, joy, keyboard_)

                # ! wait for response
                while True:
                    keys = get_keypresses(joy, keyboard_)
                    if keys:
                        decision_time = cue_decision_clock.getTime()
                        if i == num_of_cues - 1 and keys == ["down"]:
                            # at the last cue you cannot press down
                            win.flip()
                            continue
                        behavioral_data[f"cue{i+1}_decision_time"] = decision_time
                        break
                    data_saver.check_exit()
                    win.flip()
                if "down" in keys:
                    cues_taken += 1
                elif "left" in keys:
                    behavioral_data["choice"] = "A"
                    break
                elif "right" in keys:
                    behavioral_data["choice"] = "B"
                    break

            behavioral_data["total_decision_time"] = total_decision_clock.getTime()
            behavioral_data["cues_taken"] = cues_taken

            # ! clear
            stimulus["right_arrow"].setAutoDraw(False)
            stimulus["left_arrow"].setAutoDraw(False)
            stimulus["down_arrow"].setAutoDraw(False)
            stimulus["left_square"].setAutoDraw(False)
            stimulus["right_square"].setAutoDraw(False)
            stimulus["middle_text"].setAutoDraw(False)
            stimulus["left_text"].setAutoDraw(False)
            stimulus["right_text"].setAutoDraw(False)
            win.flip()

            # ! rate confidence

            wait_for_no_keys_pressed(win, joy, keyboard_)
            behavioral_data["confidence"] = get_value_from_slider(
                slider_confidence,
                "Pewność",
                win,
                data_saver,
                stimulus,
                config["Slider_speed"],
                joy,
                keyboard_,
            )

            # check if choice is correct
            if behavioral_data["choice"] == trial["correct"]:
                behavioral_data["choice_correct"] = True
            else:
                behavioral_data["choice_correct"] = False

            if config["Show_feedback"]:
                # ! give feedback
                if behavioral_data["choice_correct"]:
                    feedback = stimulus["feedback_good"]
                    trigger_type = TriggerTypes.FEEDB_GOOD
                else:
                    feedback = stimulus["feedback_bad"]
                    trigger_type = TriggerTypes.FEEDB_BAD

                feedback_show_time = random.uniform(*config["Feedback_show_time"])
                feedback.setAutoDraw(True)

                trigger_handler.prepare_trigger(
                    trigger_type=trigger_type,
                    block_type=block["type"],
                )
                win.flip()
                trigger_handler.send_trigger()

                core.wait(feedback_show_time)
                feedback.setAutoDraw(False)
                win.flip()
                data_saver.check_exit()

            # ! save behavioral data
            data_saver.beh.append(behavioral_data)
            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.data(f"Trial data: {trial}\n")
            logging.flush()
