#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random

from classes.experiment_info import display_eeg_info, get_participant_info

# from classes.prepare_experiment import prepare_trials, create_stops_times_dict, randomize_buttons
from classes.load_data import load_config, load_data
from classes.ophthalmic_procedure import ophthalmic_procedure
from classes.save_data import save_beh, save_triggers
from classes.screen import create_win
from classes.show import show
from classes.show_info import show_info
from classes.triggers import create_eeg_port

__author__ = ["ociepkam", "filyp"]


def run():
    # Load config
    config = load_config()

    display_eeg_info()
    participant_info = get_participant_info(config["Observer"])
    # participant_info = "mock_info"

    # EEG triggers
    if config["Send_EEG_trigg"]:
        port_eeg = create_eeg_port()
    else:
        port_eeg = None

    # screen
    win, screen_res, frames_per_sec = create_win(screen_color=config["Screen_color"])

    # Run experiment
    # Ophthalmic procedure
    triggers_list = list()
    trigger_no = 0
    if config["Ophthalmic_procedure"]:
        trigger_no, triggers_list = ophthalmic_procedure(
            win=win,
            send_eeg_triggers=config["Send_EEG_trigg"],
            screen_res=screen_res,
            frames_per_sec=frames_per_sec,
            port_eeg=port_eeg,
            trigger_no=trigger_no,
            triggers_list=triggers_list,
            text_size=config["Text_size"],
        )

    # Instruction
    instructions = sorted([f for f in os.listdir("messages") if f.startswith("instruction")])
    for instruction in instructions:
        show_info(
            win=win,
            file_name=instruction,
            text_size=config["Text_size"],
            screen_width=screen_res["width"],
            participant_info=participant_info,
            beh=[],
            triggers_list=triggers_list,
        )

    # load stimulus
    stimulus = load_data(win=win, folder_name="stimulus", config=config, screen_res=screen_res)

    # Experiment
    beh, triggers_list = show(
        win=win,
        screen_res=screen_res,
        stimulus=stimulus,
        config=config,
        participant_info=participant_info,
        port_eeg=port_eeg,
        trigger_no=trigger_no,
        triggers_list=triggers_list,
        frame_time=1.0 / frames_per_sec,
    )

    # Save data
    save_beh(data=beh, name=participant_info)
    save_triggers(data=triggers_list, name=participant_info)


run()
