import os
import random

import pandas as pd
from psychopy import logging, visual


def prepare_trials(block, config, win):
    all_trials = []

    filename = os.path.join("input_data", "diamond_task", block["info_file"])
    trials_info = pd.read_excel(filename)

    for row in trials_info.itertuples():
        image_path = os.path.join(config["Photos_directory"], row.IAPSslide)
        image = visual.ImageStim(
            win=win,
            image=image_path,
            # size=config["Image_size"],
            name=row.IAPSslide,
        )
        all_trials.append(
            dict(
                correct=row.Correct,
                image=image,
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
