import os
import random
from collections import OrderedDict

import numpy as np
from psychopy import core, event, logging, visual
from psychopy.hardware import joystick, keyboard

from classes.show_info import show_info, read_text_from_file
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
    slider, text, win, data_saver, stimulus, speed=1, joy=None, keyboard=None, manikins=[]
):
    slider.markerPos = 50
    for manikin in manikins:
        manikin.setAutoDraw(True)
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

    for manikin in manikins:
        manikin.setAutoDraw(False)
    slider.setAutoDraw(False)
    stimulus["top_text"].setAutoDraw(False)
    win.flip()
    return slider.markerPos


def random_time(min_time, max_time, step):
    possible_times = np.arange(min_time, max_time + step, step)
    return random.choice(possible_times)


def diamond_task(
    win,
    screen_res,
    config,
    data_saver,
):
    # frame_rate = win.getActualFrameRate()
    # logging.info(f"Frame rate: {frame_rate}")

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
    global_clock = core.Clock()

    # load stimulus
    stimulus = load_stimuli(win=win, config=config, screen_res=screen_res)

    slider_params = dict(
        win=win,
        size=(0.9, 0.03),
        ticks=[0, 100],
        borderColor=config["Text_color"],
        markerColor=config["Text_color"],
        # labels=["0", "100"],
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

    # ! mark the start of the experiment
    trigger_handler.prepare_trigger(
        trigger_type=TriggerTypes.EXPERIMENT_START,
    )
    trigger_handler.send_trigger()
    global_clock.reset()

    for block in config["Experiment_blocks"]:
        trigger_handler.prepare_trigger(
            trigger_type=TriggerTypes.BLOCK_START,
            block_type=block["type"],
        )
        trigger_handler.send_trigger()
        logging.data(f"Entering block: {block}")
        logging.flush()

        if block["type"] == "break":
            text = read_text_from_file(os.path.join("messages", block["file_name"]))
            if len(text) < 70:
                alignText = "center"
            else:
                alignText = "left"

            if "image" not in block:
                show_info(
                    win=win,
                    file_name=block["file_name"],
                    config=config,
                    screen_width=1.3,
                    data_saver=data_saver,
                    alignText=alignText,
                )
                continue
            elif "image" in block:
                image = visual.ImageStim(
                    win=win,
                    image=os.path.join("input_data", "diamond_task", block["image"]),
                    size=(0.557, 1),
                    pos=(-0.5, 0),
                )
                image.setAutoDraw(True)
                show_info(
                    win=win,
                    file_name=block["file_name"],
                    config=config,
                    screen_width=0.8,
                    data_saver=data_saver,
                    alignText=alignText,
                    pos=(0.3, 0),
                )
                image.setAutoDraw(False)
                win.flip()
                continue
        elif block["type"] in ["experiment", "training"]:
            block["trials"] = prepare_trials(block, config, win)
        elif block["type"] == "resting_state":
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            core.wait(block["seconds"])
            stimulus["fixation"].setAutoDraw(False)
            win.flip()
            data_saver.check_exit()
        else:
            raise Exception(
                "{} is bad block type in config Experiment_blocks".format(block["type"])
            )

        for trial in block["trials"]:
            behavioral_data = OrderedDict(
                block_type=block["type"],
                choice=None,
                correct_choice=trial["correct"],
                is_choice_correct=None,
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
                image_abs_time=None,
                arousal_slider_abs_time=None,
                valence_slider_abs_time=None,
                choice_prompt_abs_time=None,
                cue1_abs_time=None,
                cue2_abs_time=None,
                cue3_abs_time=None,
                cue4_abs_time=None,
                cue5_abs_time=None,
                cue6_abs_time=None,
                confidence_slider_abs_time=None,
                feedback_abs_time=None,
            )
            wait_for_no_keys_pressed(win, joy, keyboard_)

            # ! show empty screen between trials
            blank_screen_time = random_time(*config["Empty_screen_between_trials"])
            win.flip()
            core.wait(blank_screen_time)
            data_saver.check_exit()

            # ! show fixation
            fixation_show_time = random_time(*config["Fixation_show_time"])
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            core.wait(fixation_show_time)
            stimulus["fixation"].setAutoDraw(False)
            win.flip()
            data_saver.check_exit()

            if config["Show_images"]:
                # ! show image
                behavioral_data["image"] = trial["image"].name
                photo_show_time = random_time(*config["Photo_show_time"])
                trial["image"].setAutoDraw(True)
                trigger_handler.prepare_trigger(
                    trigger_type=TriggerTypes.IMAGE,
                    block_type=block["type"],
                )
                win.flip()
                trigger_handler.send_trigger()
                behavioral_data["image_abs_time"] = global_clock.getTime()
                core.wait(photo_show_time)
                trial["image"].setAutoDraw(False)
                win.flip()
                data_saver.check_exit()

            if config["Rate_arousal"]:
                # ! rate arousal
                arousal_manikins = [
                    stimulus["arousal1"],
                    stimulus["arousal2"],
                    stimulus["arousal3"],
                    stimulus["arousal4"],
                    stimulus["arousal5"],
                ]
                behavioral_data["arousal_slider_abs_time"] = global_clock.getTime()
                behavioral_data["arousal"] = get_value_from_slider(
                    slider_arousal,
                    "Pobudzenie",
                    win,
                    data_saver,
                    stimulus,
                    config["Slider_speed"],
                    joy,
                    keyboard_,
                    arousal_manikins,
                )

            if config["Rate_valence"]:
                # ! rate valence
                valence_manikins = [
                    stimulus["valence1"],
                    stimulus["valence2"],
                    stimulus["valence3"],
                    stimulus["valence4"],
                    stimulus["valence5"],
                ]
                behavioral_data["valence_slider_abs_time"] = global_clock.getTime()
                behavioral_data["valence"] = get_value_from_slider(
                    slider_valence,
                    "Nastrój",
                    win,
                    data_saver,
                    stimulus,
                    config["Slider_speed"],
                    joy,
                    keyboard_,
                    valence_manikins,
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
            behavioral_data["choice_prompt_abs_time"] = global_clock.getTime()

            participants_choice = None

            # ! wait for response
            while True:
                keys = get_keypresses(joy, keyboard_)
                if keys:
                    behavioral_data["choice_prompt_decision_time"] = cue_decision_clock.getTime()
                    break
                data_saver.check_exit()
                win.flip()
            if "left" in keys:
                participants_choice = "A"
            if "right" in keys:
                participants_choice = "B"
            wait_for_no_keys_pressed(win, joy, keyboard_)

            cues_taken = 1
            num_of_cues = len(trait_names)
            for i, trait_name, info_pair in zip(
                range(num_of_cues), trait_names, trial["diamond_data"]
            ):
                if participants_choice is not None:
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
                behavioral_data[f"cue{i+1}_abs_time"] = global_clock.getTime()

                info_show_time = random_time(*config["Diamond_info_show_time"])
                core.wait(info_show_time)
                data_saver.check_exit()

                # ! cue prompt
                stimulus["right_arrow"].setAutoDraw(True)
                stimulus["left_arrow"].setAutoDraw(True)
                stimulus["down_arrow"].setAutoDraw(True)
                stimulus["left_square"].setAutoDraw(True)
                stimulus["right_square"].setAutoDraw(True)
                stimulus["left_text"].setAutoDraw(True)
                stimulus["right_text"].setAutoDraw(True)
                stimulus["middle_text"].setAutoDraw(False)
                stimulus["left_text"].text = "A"
                stimulus["right_text"].text = "B"
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
                    participants_choice = "A"
                    break
                elif "right" in keys:
                    participants_choice = "B"
                    break

            behavioral_data["total_decision_time"] = total_decision_clock.getTime()
            behavioral_data["cues_taken"] = cues_taken
            behavioral_data["choice"] = participants_choice

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

            # ! show empty screen between choice and confidence rating
            blank_screen_time = random_time(*config["Blank_between_choice_and_confidence_rating"])
            win.flip()
            core.wait(blank_screen_time)
            data_saver.check_exit()

            # ! rate confidence
            wait_for_no_keys_pressed(win, joy, keyboard_)
            behavioral_data["confidence_slider_abs_time"] = global_clock.getTime()
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
            if participants_choice == trial["correct"]:
                behavioral_data["is_choice_correct"] = True
            else:
                behavioral_data["is_choice_correct"] = False

            if config["Show_feedback"]:
                # ! show empty screen between confidence rating and feedback
                blank_screen_time = random_time(
                    *config["Blank_between_confidence_rating_and_feedback"]
                )
                win.flip()
                core.wait(blank_screen_time)
                data_saver.check_exit()

                # ! give feedback
                if behavioral_data["is_choice_correct"]:
                    feedback = stimulus["feedback_good"]
                    trigger_type = TriggerTypes.FEEDB_GOOD
                else:
                    feedback = stimulus["feedback_bad"]
                    trigger_type = TriggerTypes.FEEDB_BAD

                feedback_show_time = random_time(*config["Feedback_show_time"])
                feedback.setAutoDraw(True)

                trigger_handler.prepare_trigger(
                    trigger_type=trigger_type,
                    block_type=block["type"],
                )
                win.flip()
                trigger_handler.send_trigger()
                behavioral_data["feedback_abs_time"] = global_clock.getTime()

                core.wait(feedback_show_time)
                feedback.setAutoDraw(False)
                win.flip()
                data_saver.check_exit()

            # ! save behavioral data
            data_saver.beh.append(behavioral_data)
            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.data(f"Trial data: {trial}\n")
            logging.flush()
