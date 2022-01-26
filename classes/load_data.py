import codecs
import os

import yaml
from psychopy import visual

possible_images_format = ("bmp", "jpg", "png", "gif")
possible_audio_format = ("mp3", "au", "mp2", "wav", "wma", "ogg")


def load_config(config_path):
    try:
        with open(config_path) as yaml_file:
            doc = yaml.safe_load(yaml_file)
        return doc
    except:
        raise Exception("Can't load config file")


def load_stimuli(win, folder_name, config, screen_res):
    """
    ladowanie tekstu, zdjec i dzwiekow
    :param screen_res:
    :param config:
    :param win: visual.Window z psychopy
    :param folder_name: nazwa folderu z ktorego beda ladowane pliki
    """

    orientation = config.get("Orientation", "horizontal")
    if orientation == "horizontal":
        rotation = 0
    elif orientation == "vertical":
        rotation = 90
    else:
        raise Exception("Wrong orientation")

    stimuli = dict()
    stimuli["fixation"] = visual.TextStim(
        win,
        color=config["Text_color"],
        text="+",
        height=2 * config["Fixation_size"],
        pos=(0, 0),
        ori=rotation,
        name="fixation",
    )

    path = os.path.join(folder_name, "flankers.txt")
    with open(path, "r") as text_file:
        for line in text_file:
            stimulus_name = line.split(":")[0]
            text = line.split(":")[1]
            text = text.split("\n")[0]
            stimuli[stimulus_name] = visual.TextStim(
                win=win,
                antialias=True,
                font=config["Font"],
                text=text,
                height=config["Flanker_size"],
                wrapWidth=screen_res["width"],
                color=config["Text_color"],
                ori=rotation,
                name=stimulus_name,
            )

    # create cues
    if config["Cues"] is not None:
        cue1_text, cue2_text = config["Cues"]
        cue1 = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Font"],
            text=cue1_text,
            height=config["Text_size"],
            wrapWidth=screen_res["width"],
            color=config["Text_color"],
            name="cue1",
        )
        cue2 = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Font"],
            text=cue2_text,
            height=config["Text_size"],
            wrapWidth=screen_res["width"],
            color=config["Text_color"],
            name="cue2",
        )
    else:
        cue1 = None
        cue2 = None
    stimuli["cue1"] = cue1
    stimuli["cue2"] = cue2

    return stimuli


def read_text_from_file(file_name, insert=""):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert: dynamically generated info
    :return: message
    """
    if not isinstance(file_name, str):
        raise TypeError("file_name must be a string")
    msg = list()
    with codecs.open(file_name, encoding="utf-8", mode="r") as data_file:
        for line in data_file:
            if not line.startswith("#"):  # if not commented line
                if line.startswith("<--insert-->"):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return "".join(msg)
