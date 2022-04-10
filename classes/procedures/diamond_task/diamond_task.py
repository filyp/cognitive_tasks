import random
from collections import OrderedDict

import numpy as np
from psychopy import core, event, logging, visual
from psychopy.hardware import joystick

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


def get_value_from_slider(slider, text, win, mouse, data_saver, stimulus, speed=1, joy=None):
    if joy is None:
        slider.reset()
        stimulus["slider_button"].setAutoDraw(True)
        stimulus["slider_button_text"].setAutoDraw(True)
    else:
        slider.markerPos = 50
    stimulus["top_text"].setAutoDraw(True)
    stimulus["top_text"].text = text
    win.flip()

    if joy is None:
        while not (slider.getRating() and mouse.isPressedIn(stimulus["slider_button"])):
            slider.draw()
            win.flip()
            data_saver.check_exit()
    else:
        # joystick is connected, so use it to move marker
        while True:
            pressed = get_joystick_input(joy)
            if "left" in pressed:
                slider.markerPos -= speed
            if "right" in pressed:
                slider.markerPos += speed
            if "down" in pressed:
                break
            slider.draw()
            win.flip()
            data_saver.check_exit()
        while "down" in get_joystick_input(joy):
            win.flip()

    stimulus["slider_button"].setAutoDraw(False)
    stimulus["slider_button_text"].setAutoDraw(False)
    stimulus["top_text"].setAutoDraw(False)
    win.flip()
    return slider.getRating()


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
    else:
        joy = None

    mouse = event.Mouse(win=win, visible=False)
    total_decision_clock = core.Clock()
    cue_decision_clock = core.Clock()

    # load stimulus
    stimulus = load_stimuli(win=win, config=config, screen_res=screen_res)

    slider_params = dict(
        win=win,
        size=(screen_res["width"] * 0.3, screen_res["height"] * 0.03),
        ticks=[0, 100],
        borderColor=config["Text_color"],
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
            block["trials"] = prepare_trials(block, stimulus)
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
                cues_decision_time=[],
                number_of_cues=None,
            )

            # ! show empty screen between trials
            min_time, max_time, step = config["Empty_screen_between_trials"]
            possible_times = np.arange(min_time, max_time + step, step)
            empty_screen_between_trials = random.choice(possible_times)
            win.flip()
            core.wait(empty_screen_between_trials)
            data_saver.check_exit()

            # ! show fixation
            fixation_show_time = random.uniform(*config["Fixation_show_time"])
            stimulus["fixation"].setAutoDraw(True)
            win.flip()
            core.wait(fixation_show_time)
            stimulus["fixation"].setAutoDraw(False)
            data_saver.check_exit()

            if config["Show_photo"]:
                # ! show photo
                # ...
                pass

            if config["Rate_arousal"]:
                # ! rate arousal
                behavioral_data["arousal"] = get_value_from_slider(
                    slider_arousal,
                    "Pobudzenie",
                    win,
                    mouse,
                    data_saver,
                    stimulus,
                    config["Slider_speed"],
                    joy,
                )

            if config["Rate_valence"]:
                # ! rate valence
                behavioral_data["valence"] = get_value_from_slider(
                    slider_valence,
                    "Nastrój",
                    win,
                    mouse,
                    data_saver,
                    stimulus,
                    config["Slider_speed"],
                    joy,
                )

            # ! decision
            total_decision_clock.reset()
            cue_decision_clock.reset()
            for trait_name, info_pair in zip(trait_names, trial["diamond_data"]):
                # ! choice prompt
                stimulus["right_arrow"].setAutoDraw(True)
                stimulus["left_arrow"].setAutoDraw(True)
                stimulus["down_arrow"].setAutoDraw(True)

                stimulus["left_square"].setAutoDraw(False)
                stimulus["right_square"].setAutoDraw(False)
                stimulus["middle_text"].setAutoDraw(False)
                stimulus["left_text"].setAutoDraw(False)
                stimulus["right_text"].setAutoDraw(False)

                if trait_name == trait_names[0]:
                    stimulus["left_square"].setAutoDraw(True)
                    stimulus["right_square"].setAutoDraw(True)
                    stimulus["middle_text"].setAutoDraw(True)
                    stimulus["left_text"].setAutoDraw(True)
                    stimulus["right_text"].setAutoDraw(True)
                    stimulus["middle_text"].text = ""
                    stimulus["left_text"].text = "A"
                    stimulus["right_text"].text = "B"
                elif trait_name == trait_names[-1]:
                    stimulus["down_arrow"].setAutoDraw(False)
                win.flip()

                # ! wait for response
                event.clearEvents()
                while True:
                    if config["Keys"] == "arrows":
                        keys = event.getKeys(keyList=["down", "left", "right"])
                    elif config["Keys"] == "joystick":
                        keys = get_joystick_input(joy)

                    if keys:
                        if trait_name == trait_names[-1] and keys == ["down"]:
                            # at the last cue you cannot press down
                            win.flip()
                            continue
                        behavioral_data["cues_decision_time"].append(cue_decision_clock.getTime())
                        break
                    data_saver.check_exit()
                    win.flip()
                if "down" in keys:
                    pass
                elif "left" in keys:
                    behavioral_data["choice"] = "A"
                    break
                elif "right" in keys:
                    behavioral_data["choice"] = "B"
                    break

                # ! show diamond info
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
                win.flip()
                cue_decision_clock.reset()
                info_show_time = random.uniform(*config["Diamond_info_show_time"])
                core.wait(info_show_time)
                data_saver.check_exit()
            behavioral_data["total_decision_time"] = total_decision_clock.getTime()
            behavioral_data["number_of_cues"] = len(behavioral_data["cues_decision_time"])

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
            if config["Keys"] == "joystick":
                # make sure joystick is unpressed
                while get_joystick_input(joy) != []:
                    win.flip()
            behavioral_data["confidence"] = get_value_from_slider(
                slider_confidence,
                "Pewność",
                win,
                mouse,
                data_saver,
                stimulus,
                config["Slider_speed"],
                joy,
            )

            # check if choice is correct
            if behavioral_data["choice"] == trial["correct"]:
                behavioral_data["choice_correct"] = True
            else:
                behavioral_data["choice_correct"] = False

            if config["Show_feedback"]:
                # ! give feedback
                # ...
                pass

            # ! save behavioral data
            # behavioral_data = OrderedDict(
            #     block_type=block["type"],
            #     trial_type=trial["type"],
            #     cue_name=cue_name,
            #     target_name=trial["target"].name,
            #     response=response,
            #     rt=reaction_time,
            #     reaction=reaction,
            #     threshold_rt=feedback_timer.thresholds[cue_name] if config["Show_feedback"] else None,
            #     empty_screen_between_trials=empty_screen_between_trials,
            #     cue_show_time=cue_show_time if config["Show_cues"] else None,
            #     empty_screen_after_cue_show_time=empty_screen_after_cue_show_time if config["Show_cues"] else None,
            #     fixation_show_time=fixation_show_time,
            # )
            data_saver.beh.append(behavioral_data)
            logging.data(f"Behavioral data: {behavioral_data}\n")
            logging.data(f"Trial data: {trial}\n")
            logging.flush()
