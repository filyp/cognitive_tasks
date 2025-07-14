import os
from pathlib import Path
from typing import OrderedDict

import pandas as pd
from psychopy import core, event, logging, visual

from classes.load_data import load_data
from classes.show_info import show_text
from classes.triggers_common import TriggerHandler, create_eeg_port

text_path = Path("messages") / "topological_task"


def get_trigger_name(row, training, event):
    """example triggers:
    TR*FIX*A*NA-7*{}
    EX*RES*NA*NA-7*{}
    """
    stem = row["file_name"].split(".")[0]
    return (
        # f"{'TR' if training else 'EX'}*{event}*{row['image_type']}*{row['shown_word']}*"
        f"{'TR' if training else 'EX'}*{event}*{row['image_type']}*{stem}*"
        + "{}"
    )


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
    na_stim = visual.TextStim(
        win,
        color="black",
        text="NA",
        height=config["Word_size"],
        pos=(0, 0),
    )
    w_stim = visual.TextStim(
        win,
        color="black",
        text="W",
        height=config["Word_size"],
        pos=(0, 0),
    )
    side = 1 if yes_key == "rctrl" else -1
    dist = config["Yes_no_stim_distance"]
    yes_option = visual.TextStim(
        win,
        color="green",
        text="TAK",
        pos=(side * dist, -dist),
        height=config["Yes_no_stim_height"],
        font=config["Text"]["font"],
    )
    no_option = visual.TextStim(
        win,
        color="red",
        text="NIE",
        pos=(-side * dist, -dist),
        height=config["Yes_no_stim_height"],
        font=config["Text"]["font"],
    )

    def trial(row, training):
        trigger_handler.open_trial()
        image_id = row["file_name"].split(".")[0]

        # ! prepare stimuli
        pre_question = f"""\
Za chwilę zobaczysz {row["celownik"]}.
Gdzie {row["jest"]} {row["przedmiot"]}?"""
        post_question = f"""\
Czy poniższy wyraz poprawnie opisuje
położenie {row["dopelniacz"]} w stosunku
do czarnego przedmiotu?"""

        pre_question_stim = visual.TextStim(
            win, text=pre_question, pos=(0, 0), **config["Text"]
        )
        post_question_stim = visual.TextStim(
            win, text=post_question, pos=(0, 0.14), **config["Text"]
        )

        # ! show pre-question
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "QUES"))
        pre_question_stim.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Pre_question_show_time"])
        pre_question_stim.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        # ! show first fixation
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "FIX1"))
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["First_fixation_show_time"])
        fixation.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        # ! show image
        image = images_dict[image_id]
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "IMAG"))
        image.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Image_show_time"])
        image.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        # ! show second fixation
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "FIX2"))
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Second_fixation_show_time"])
        fixation.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        # ! show word
        word_stim = na_stim if row["shown_word"] == "NA" else w_stim
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "WORD"))
        word_stim.setAutoDraw(True)
        if training:
            post_question_stim.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Word_show_time"])
        data_saver.check_exit()

        # ! response
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "WAIT"))
        yes_option.setAutoDraw(True)
        no_option.setAutoDraw(True)
        event.clearEvents()
        win.callOnFlip(clock.reset)
        win.flip()
        trigger_handler.send_trigger()
        keys = event.waitKeys(
            keyList=[yes_key, no_key],
            maxWait=config["Maximal_response_time"] if not training else float("inf"),
        )
        if keys:
            reaction_time = clock.getTime()
            key_pressed = keys[0]
            trigger_handler.prepare_trigger(get_trigger_name(row, training, "RESP"))
            trigger_handler.send_trigger()
        else:
            reaction_time = None
            key_pressed = None
        yes_option.setAutoDraw(False)
        no_option.setAutoDraw(False)
        word_stim.setAutoDraw(False)
        if training:
            post_question_stim.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        # ! show third fixation
        trigger_handler.prepare_trigger(get_trigger_name(row, training, "FIX3"))
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Third_fixation_show_time"])
        fixation.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        yes_or_no = None
        if key_pressed == yes_key:
            yes_or_no = "yes"
        elif key_pressed == no_key:
            yes_or_no = "no"

        # ! check if answer is valid
        if row["image_type"] == "a":
            answer_valid = True
        else:
            consistent = row["image_type"] == row["shown_word"].lower()
            if consistent:
                answer_valid = yes_or_no == "yes"
            else:
                answer_valid = yes_or_no == "no"
        if key_pressed is None:
            answer_valid = False

        # ! close the trial
        behavioral_data = OrderedDict(
            training=training,
            reaction_time=reaction_time,
            key_pressed=key_pressed,
            answer_valid=answer_valid,
            yes_or_no=yes_or_no,
            **row,
        )
        data_saver.beh.append(behavioral_data)
        trigger_handler.close_trial(value=yes_or_no)
        data_saver.check_exit()

    text_vals = {
        "yes_key_text": config["key_names"][yes_key],
        "no_key_text": config["key_names"][no_key],
    }

    # ! run the procedure ####################################

    # * instructions
    for instr_file in [
        "instr1.txt",
        "instr2.txt",
        "instr3.txt",
        "instr4.txt",
    ]:
        text = (text_path / instr_file).read_text().format(**text_vals)
        show_text(text, win, data_saver, **config["Text"])

    # * training
    # for training, use some 6 non-ambiguous trials
    df = pd.read_csv(
        os.path.join("input_data", "topological_task_training.csv"),
        keep_default_na=False,  # "NA" strings are not NaN!
    )
    for _, row in df.iterrows():
        trial(row, training=True)

    text = (text_path / "instr5.txt").read_text().format(**text_vals)
    show_text(text, win, data_saver, **config["Text"])

    df = pd.read_csv(
        os.path.join("input_data", "topological_task_shuffled.csv"),
        keep_default_na=False,  # "NA" strings are not NaN!
    )
    for i, row in df.iterrows():
        if config["Experiment_version"] == "B":
            # * reverse word
            row["shown_word"] = "NA" if row["shown_word"] == "W" else "W"

        trial(row, training=False)

        if i % 24 == 0 and i != 0:
            # * break
            text = (text_path / "break.txt").read_text().format(**text_vals)
            show_text(text, win, data_saver, **config["Text"])
