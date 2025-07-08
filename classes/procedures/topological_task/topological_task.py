import os
import time
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
    if config["Random_condition"] == 1:
        yes_key, no_key = "lctrl", "rctrl"
    elif config["Random_condition"] == 2:
        yes_key, no_key = "rctrl", "lctrl"
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
        event.clearEvents()
        win.callOnFlip(clock.reset)
        win.flip()
        trigger_handler.send_trigger()
        keys = event.waitKeys(
            keyList=[yes_key, no_key],
            maxWait=config["Maximal_response_time"],
        )
        reaction_time = clock.getTime()
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

    return
