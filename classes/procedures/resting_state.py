import os
import time

from psychopy import core, event, logging, visual

from classes.show_info import read_text_from_file
from classes.triggers_common import create_eeg_port, simple_send_trigger


def resting_state(
    win,
    screen_res,
    config,
    data_saver,
):
    clock = core.Clock()

    # EEG triggers
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    # trigger_handler = TriggerHandler(port_eeg, data_saver=data_saver)

    fixation = visual.ImageStim(
        win=win,
        image=os.path.join("input_data", "+.png"),
        size=config["Fixation_size"],
        name="fixation",
        interpolate=True,
    )

    text = read_text_from_file(os.path.join("messages", "resting_state", "open.txt"))
    open_eyes_stim = visual.TextStim(
        win=win,
        antialias=True,
        font=config["Text_font"],
        text=text,
        height=config["Text_size"],
        color=config["Text_color"],
    )
    open_eyes_stim.setAutoDraw(True)
    clock.reset()
    while clock.getTime() < config["Command_show_time"]:
        data_saver.check_exit()
        win.flip()
    open_eyes_stim.setAutoDraw(False)

    simple_send_trigger(port_eeg, 1)

    fixation.setAutoDraw(True)
    clock.reset()
    while clock.getTime() < config["Open_eyes_duration"]:
        data_saver.check_exit()
        win.flip()
    fixation.setAutoDraw(False)
    
    simple_send_trigger(port_eeg, 2)

    text = read_text_from_file(os.path.join("messages", "resting_state", "closed.txt"))
    closed_eyes_stim = visual.TextStim(
        win=win,
        antialias=True,
        font=config["Text_font"],
        text=text,
        height=config["Text_size"],
        color=config["Text_color"],
    )
    closed_eyes_stim.setAutoDraw(True)
    clock.reset()
    while clock.getTime() < config["Command_show_time"]:
        data_saver.check_exit()
        win.flip()
    closed_eyes_stim.setAutoDraw(False)

    simple_send_trigger(port_eeg, 3)

    clock.reset()
    while clock.getTime() < config["Closed_eyes_duration"]:
        data_saver.check_exit()
        win.flip()

    simple_send_trigger(port_eeg, 4)