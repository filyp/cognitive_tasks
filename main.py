# -*- coding: utf-8 -*-
# how to run:
# venv/bin/python main.py config/some_task.yaml

import os
import sys

import yaml
from psychopy import logging

logging.console.setLevel(logging.DATA)

from classes.experiment_info import get_participant_info

from classes.save_data import DataSaver
from classes.screen import create_win

# from classes.procedures.ophthalmic_procedure import ophthalmic_procedure
from classes.procedures.flanker_task.flanker_task import flanker_task
from classes.procedures.diamond_task.diamond_task import diamond_task

__author__ = ["ociepkam", "filyp"]


def load_config(config_path):
    try:
        with open(config_path) as yaml_file:
            doc = yaml.safe_load(yaml_file)
        return doc
    except:
        raise Exception("Can't load config file")


def run():
    # Load config
    config_path = sys.argv[1]
    config = load_config(config_path)
    experiment_name = os.path.split(config_path)[-1]
    experiment_name = experiment_name.split(".")[0]

    participant_info = get_participant_info()
    # participant_info = "mock_info"  # TODO reenable after testing

    data_saver = DataSaver(participant_info, experiment_name, beh=[], triggers_list=[])

    # screen
    win, screen_res, frames_per_sec = create_win(screen_color=config["Screen_color"])
    logging.data(f"frames per second = {frames_per_sec}")

    # # Ophthalmic procedure
    # if config["Ophthalmic_procedure"]:
    #     trigger_no, triggers_list = ophthalmic_procedure(
    #         win=win,
    #         send_eeg_triggers=config["Send_EEG_trigg"],
    #         screen_res=screen_res,
    #         frames_per_sec=frames_per_sec,
    #         port_eeg=port_eeg,
    #         trigger_no=trigger_no,
    #         triggers_list=triggers_list,
    #         text_size=config["Text_size"],
    #         text_color=config["Text_color"],
    #         data_saver=data_saver,
    #     )

    # choose which procedure to run
    procedure = {
        "Flanker task": flanker_task,
        "Diamond task": diamond_task,
    }[config["Procedure"]]

    # Experiment
    procedure(
        win=win,
        screen_res=screen_res,
        config=config,
        data_saver=data_saver,
    )

    # Save data
    data_saver.save_beh()
    data_saver.save_triggers()


run()
