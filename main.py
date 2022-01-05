#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random

# from classes.prepare_experiment import prepare_trials, create_stops_times_dict, randomize_buttons
from classes.load_data import load_data, load_config
from classes.screen import create_win
from classes.experiment_info import experiment_info, eeg_info
from classes.ophthalmic_procedure import ophthalmic_procedure
from classes.show import show
from classes.save_data import save_beh, save_triggers
from classes.triggers import create_eeg_port
from classes.show_info import show_info
from classes.prepare_experiment import prepare_experiment

__author__ = 'ociepkam'


def run():
    # Prepare experiment
    config = load_config()
    eeg_info()
    part_id, sex, age, date = experiment_info(config['Observer'])
    date = date.replace(":", "-")
    part_name = "{}_{}_{}_{}".format(part_id, sex, age, date)
    # EEG triggers
    if config['Send_EEG_trigg']:
        port_eeg = create_eeg_port()
    else:
        port_eeg = None

    triggers_list = list()
    trigger_no = 0

    # screen
    win, screen_res, frames_per_sec = create_win(screen_color=config['Screen_color'])

    # load stimulus
    stimulus = load_data(win=win, folder_name="stimulus", config=config, screen_res=screen_res)

    # prepare experiment
    experiment = prepare_experiment(config['Experiment_blocks'], stimulus)
    # Run experiment
    # Ophthalmic procedure
    if config['Ophthalmic_procedure']:
        trigger_no, triggers_list = ophthalmic_procedure(win=win, send_eeg_triggers=config['Send_EEG_trigg'],
                                                         screen_res=screen_res, frames_per_sec=frames_per_sec,
                                                         port_eeg=port_eeg, trigger_no=trigger_no,
                                                         triggers_list=triggers_list, text_size=config['Text_size'])

    # Instruction
    instructions = sorted([f for f in os.listdir('messages') if f.startswith('instruction')])
    for instruction in instructions:
        show_info(win=win, file_name=instruction, text_size=config['Text_size'], screen_width=screen_res['width'],
                  part_id=part_name, beh=[], triggers_list=triggers_list)

    # Experiment
    beh, triggers_list = show(win=win, screen_res=screen_res, experiment=experiment, config=config, part_id=part_id,
                              port_eeg=port_eeg, trigger_no=trigger_no, triggers_list=triggers_list,
                              frame_time=1. / frames_per_sec)

    # Save data
    save_beh(data=beh, name=part_name)
    save_triggers(data=triggers_list, name=part_name)


run()
