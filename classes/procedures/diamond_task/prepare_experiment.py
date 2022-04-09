import os
import random

import pandas as pd
from psychopy import logging


def prepare_trials(block, stimulus):
    all_trials = []

    filename = os.path.join("input_data", "diamond_task", block["info_file"])
    trials_info = pd.read_excel(filename)

    for row in trials_info.itertuples():
        all_trials.append(
            dict(
                correct=row.Correct,
                IAPSslide=row.IAPSslide,
                diamond_data=[
                    [row.Ac1, row.Bc1],
                    [row.Ac2, row.Bc2],
                    [row.Ac3, row.Bc3],
                    [row.Ac4, row.Bc4],
                    [row.Ac5, row.Bc5],
                    [row.Ac6, row.Bc6],
                ],
            )
        )

    # random.shuffle(all_trials)
    return all_trials
