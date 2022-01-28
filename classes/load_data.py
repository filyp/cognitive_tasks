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


def load_stimuli(win, config, screen_res):
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
    text_position_offset = (0, 0)

    # ! create fixation
    stimuli = dict()
    stimuli["fixation"] = visual.TextStim(
        win,
        color=config["Text_color"],
        text=config["Fixation_char"],
        font=config["Flanker_font"],
        height=config["Flanker_size"],
        pos=text_position_offset,
        ori=rotation,
        name="fixation",
    )

    # ! create targets and flankers
    r = config["Right_char"]
    l = config["Left_char"]
    stimuli_to_create = dict(
        congruent_rrr=r + r + r + r + r,
        congruent_lll=l + l + l + l + l,
        incongruent_rlr=r + r + l + r + r,
        incongruent_lrl=l + l + r + l + l,
        flankers_r=r + r + " " + r + r,
        flankers_l=l + l + " " + l + l,
    )
    for stimulus_name, text in stimuli_to_create.items():
        stimuli[stimulus_name] = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Flanker_font"],
            text=text,
            height=config["Flanker_size"],
            wrapWidth=screen_res["width"],
            color=config["Text_color"],
            ori=rotation,
            name=stimulus_name,
        )

    # ! create cues
    if config["Show_cues"]:
        cue1_text, cue2_text = config["Cues"]
        stimuli["cue1"] = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Text_font"],
            text=cue1_text,
            height=config["Text_size"],
            wrapWidth=screen_res["width"],
            color=config["Text_color"],
            name="cue1",
        )
        stimuli["cue2"] = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Text_font"],
            text=cue2_text,
            height=config["Text_size"],
            wrapWidth=screen_res["width"],
            color=config["Text_color"],
            name="cue2",
        )
    else:
        # create mock cue stimuli
        stimuli["cue1"] = visual.TextStim(win, text=None)
        stimuli["cue2"] = visual.TextStim(win, text=None)

    # ! create feedback
    if config["Show_feedback"]:
        stimuli["feedback_good"] = visual.TextStim(
            win,
            color=config["Text_color"],
            text=config["Feedback_good"],
            font=config["Feedback_font"],
            height=config["Feedback_size"],
            pos=text_position_offset,
            name="feedback_good",
        )
        stimuli["feedback_bad"] = visual.TextStim(
            win,
            color=config["Text_color"],
            text=config["Feedback_bad"],
            font=config["Feedback_font"],
            height=config["Feedback_size"],
            pos=text_position_offset,
            name="feedback_bad",
        )

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
