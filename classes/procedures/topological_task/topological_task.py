import os
import time
import random
from typing import OrderedDict

import pandas as pd
from psychopy import core, event, logging, visual

from classes.load_data import load_data
from classes.show_info import show_info
from classes.triggers_common import TriggerHandler, create_eeg_port


class TriggerTypes:
    BLOCK_START = "BLOCK_START"
    CUE = "CUE______"
    TARGET = "TARGET___"
    REACTION = "REACTION_"
    PREMATURE_EARLY_REACTION = "PREMATURE_EARLY_REACTION"
    PREMATURE_LATE_REACTION = "PREMATURE_LATE_REACTION"


def get_trigger_name(
    trigger_type,
    block,
    trial=None,
    response="{}",
):
    block_type = block["type"]
    if trial is not None:
        target_name = trial["target_name"]
        correct_side = trial["correct_side"]
    else:
        target_name = "---"
        correct_side = "-"

    return f"{trigger_type}*{block_type[:2]}*{target_name}*{correct_side}*{response}"


def topological_task(
    win,
    screen_res,
    config,
    data_saver,
):
    # ! define trigger and port handlers, and clock
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    trigger_handler = TriggerHandler(port_eeg, data_saver=data_saver)
    clock = core.Clock()

    # ! prepare response keys
    yes_key = random.choice(["lctrl", "rctrl"])
    no_key = "lctrl" if yes_key == "rctrl" else "rctrl"
    print(f"yes_key: {yes_key}, no_key: {no_key}")

    # ! load images and data
    images = load_data(
        win=win,
        folder_name=os.path.join("input_data", "topological_task"),
        config=config,
        screen_res=screen_res,
    )
    images_dict = {image["name"]: image["stimulus"] for image in images}

    fixation = visual.TextStim(
        win, color="black", text="+", height=2 * config["Fixation_size"], pos=(0, 0.006)
    )
    na_particle = visual.TextStim(
        win,
        color="black",
        text="NA",
        height=config["Particle_size"],
        pos=(0, 0),
    )
    w_particle = visual.TextStim(
        win,
        color="black",
        text="W",
        height=config["Particle_size"],
        pos=(0, 0),
    )
    side = 1 if yes_key == "rctrl" else -1
    yes_option = visual.TextStim(
        win,
        color="green",
        text="TAK",
        height=config["Text_size"],
        pos=(side * 0.2, -0.2),
    )
    no_option = visual.TextStim(
        win,
        color="red",
        text="NIE",
        height=config["Text_size"],
        pos=(-side * 0.2, -0.2),
    )

    df = pd.read_excel(os.path.join("input_data", "topological_task.xlsx"))

    # # Response options
    # response_yes = visual.TextStim(
    #     win, color="black", text="yes", height=config["Response_text_size"],
    #     pos=(0, -config["Response_text_offset"])
    # )
    # response_no = visual.TextStim(
    #     win, color="black", text="no", height=config["Response_text_size"],
    #     pos=(0, -config["Response_text_offset"] - config["Response_text_spacing"])
    # )

    # instructions #######
    for instr_file in [
        "topological_task/instr1.txt",
        "topological_task/instr2.txt",
        "topological_task/instr3.txt",
        "topological_task/instr4.txt",
    ]:
        show_info(
            win=win,
            file_name=instr_file,
            config=config,
            screen_width=screen_res["width"],
            data_saver=data_saver,
            insert_dict={
                "yes_key_text": config["key_names"][yes_key],
                "no_key_text": config["key_names"][no_key],
            },
        )

    # ! run trials
    for _, row in df.iterrows():
        trigger_handler.open_trial()

        # ! prepare stimuli
        pre_question = f"""\
Za chwilę zobaczysz {row["celownik"]}.
Gdzie {row["jest"]} {row["przedmiot"]}?"""
        post_question = f"""\
Czy poniższy wyraz poprawnie opisuje
położenie {row["dopelniacz"]} w stosunku
do czarnego przedmiotu?"""

        pre_question_stim = visual.TextStim(
            win,
            color="black",
            text=pre_question,
            height=config["Text_size"],
            pos=(0, 0),
        )
        post_question_stim = visual.TextStim(
            win,
            color="black",
            text=post_question,
            height=config["Text_size"],
            pos=(0, 0.2),
        )

        # ! show pre-question
        trigger_handler.prepare_trigger("todo_name")
        pre_question_stim.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Pre_question_show_time"])
        pre_question_stim.setAutoDraw(False)
        win.flip()

        # ! show first fixation
        trigger_handler.prepare_trigger("todo_name")
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["First_fixation_show_time"])
        fixation.setAutoDraw(False)
        win.flip()

        # ! show image
        image = images_dict["NA-22"]  # todo
        trigger_handler.prepare_trigger("todo_name")
        image.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Image_show_time"])
        image.setAutoDraw(False)
        win.flip()

        # ! show second fixation
        trigger_handler.prepare_trigger("todo_name")
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Second_fixation_show_time"])
        fixation.setAutoDraw(False)
        win.flip()

        # ! show particle
        particle = na_particle
        trigger_handler.prepare_trigger("todo_name")
        particle.setAutoDraw(True)
        post_question_stim.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Particle_show_time"])
        win.flip()

        # ! response
        trigger_handler.prepare_trigger("todo_name")
        yes_option.setAutoDraw(True)
        no_option.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Maximal_response_time"])
        # todo for loop with waiting
        yes_option.setAutoDraw(False)
        no_option.setAutoDraw(False)
        particle.setAutoDraw(False)
        post_question_stim.setAutoDraw(False)
        win.flip()

        # ! show third fixation
        trigger_handler.prepare_trigger("todo_name")
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Third_fixation_show_time"])
        fixation.setAutoDraw(False)
        win.flip()



        # ! close the trial
        behavioral_data = OrderedDict(
            # block_type=block["type"],
            # trial_type=trial["type"],
            # font_color=trial["font_color"],
            # text=trial["text"],
            # response=response_side,
            # correct_side=trial["correct_side"],
            # rt=reaction_time,
            # reaction=reaction,
            # empty_screen_show_time=empty_screen_show_time,
        )
        data_saver.beh.append(behavioral_data)
        trigger_handler.close_trial(value="-")  # todo response side
        data_saver.check_exit()


        break

    return

    reaction_time = None
    response = None

    # 1. Text prompt for 2 seconds
    # Create prompt text with image name substitution
    prompt_text = config["Prompt_text"].replace("X", trial["image_name"])
    prompt_stimulus = visual.TextStim(
        win,
        color="black",
        text=prompt_text,
        height=config["Prompt_text_size"],
        pos=(0, 0),
        wrapWidth=config["Prompt_wrap_width"],
    )

    prompt_stimulus.setAutoDraw(True)
    win.flip()
    time.sleep(config["Prompt_show_time"])
    prompt_stimulus.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()

    # 2. Fixation cross for 800 ms
    fixation.setAutoDraw(True)
    win.flip()
    time.sleep(config["Fixation_before_image_time"])
    fixation.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()

    # 3. Image for 3 seconds
    trial["image"]["stimulus"].setAutoDraw(True)
    win.flip()
    time.sleep(config["Image_show_time"])
    trial["image"]["stimulus"].setAutoDraw(False)
    data_saver.check_exit()
    win.flip()

    # 4. Fixation cross for 800 ms
    fixation.setAutoDraw(True)
    win.flip()
    time.sleep(config["Fixation_before_label_time"])
    fixation.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()

    # 5. NA or W for 1000 ms (no responses allowed)
    label_stimulus = visual.TextStim(
        win,
        color="black",
        text=trial["label"],
        height=config["Label_text_size"],
        pos=(0, 0),
    )
    label_stimulus.setAutoDraw(True)
    win.flip()

    # Clear any existing key presses
    event.clearEvents()

    # Wait for 1000ms with no responses allowed
    time.sleep(config["Label_no_response_time"])
    data_saver.check_exit()

    # 6. Response options appear below NA or W for 3 seconds or until response
    response_yes.setAutoDraw(True)
    response_no.setAutoDraw(True)
    win.callOnFlip(clock.reset)
    win.flip()

    # Collect response
    response_collected = False
    response_keys = config["Response_keys"]  # ["lctrl", "rctrl"]

    while clock.getTime() < config["Response_window_time"] and not response_collected:
        keys = event.getKeys(keyList=response_keys, timeStamped=clock)
        if keys:
            key_pressed, reaction_time = keys[0]
            response_collected = True

            # Map key to response based on participant's key mapping
            if key_pressed == config["Yes_key"]:
                response = "yes"
            elif key_pressed == config["No_key"]:
                response = "no"

            break

        data_saver.check_exit()
        win.flip()

    # Clear stimuli
    label_stimulus.setAutoDraw(False)
    response_yes.setAutoDraw(False)
    response_no.setAutoDraw(False)
    win.flip()

    # 7. Fixation cross for 800 ms before next trial
    fixation.setAutoDraw(True)
    win.flip()
    time.sleep(config["Fixation_end_trial_time"])
    fixation.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()

    # For now, just log the trial results (you can expand this later)
    print(
        f"Trial completed: Image={trial['image_name']}, Label={trial['label']}, Response={response}, RT={reaction_time}"
    )

    return {
        "image_name": trial["image_name"],
        "label": trial["label"],
        "response": response,
        "reaction_time": reaction_time,
        "expected_response": trial["expected_response"],
    }
