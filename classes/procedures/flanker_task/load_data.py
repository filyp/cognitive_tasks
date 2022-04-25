import os
from psychopy import visual

possible_images_format = ("bmp", "jpg", "png", "gif")
possible_audio_format = ("mp3", "au", "mp2", "wav", "wma", "ogg")


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

    stimuli = dict()

    # create flankers by images
    # ! create fixation
    stimuli["fixation"] = visual.ImageStim(
        win=win,
        image=os.path.join("input_data", "flanker_task", config["Fixation"]),
        size=config["Fixation_size"],
        name="fixation",
        interpolate=True,
    )

    # ! create targets and flankers
    left_ = []
    right = []
    for i in range(5):
        name = "left" + str(i)
        if config["Orientation"] == "horizontal":
            pos = (((i - 2) * config["Flanker_spacing"], 0),)
        elif config["Orientation"] == "vertical":
            pos = ((0, (i - 2) * config["Flanker_spacing"]),)

        left_.append(
            visual.ImageStim(
                win=win,
                image=os.path.join("input_data", "flanker_task", config["Arrow_left"]),
                size=config["Flanker_size"],
                pos=pos,
                name=name,
                interpolate=True,
            )
        )
        name = "right" + str(i)
        right.append(
            visual.ImageStim(
                win=win,
                image=os.path.join("input_data", "flanker_task", config["Arrow_right"]),
                size=config["Flanker_size"],
                pos=pos,
                name=name,
                interpolate=True,
            )
        )
    stimuli["congruent_rrr"] = [right[0], right[1], right[2], right[3], right[4]]
    stimuli["congruent_lll"] = [left_[0], left_[1], left_[2], left_[3], left_[4]]
    stimuli["incongruent_rlr"] = [right[0], right[1], left_[2], right[3], right[4]]
    stimuli["incongruent_lrl"] = [left_[0], left_[1], right[2], left_[3], left_[4]]
    stimuli["flankers_r"] = [right[0], right[1], right[3], right[4]]
    stimuli["flankers_l"] = [left_[0], left_[1], left_[3], left_[4]]

    # ! create cues
    if config["Show_cues"]:
        cue1_text, cue2_text = config["Cues"]
        stimuli["cue1"] = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Text_font"],
            text=cue1_text,
            height=config["Cue_size"],
            wrapWidth=screen_res["width"],
            color=config["Text_color"],
            name="cue1",
        )
        stimuli["cue2"] = visual.TextStim(
            win=win,
            antialias=True,
            font=config["Text_font"],
            text=cue2_text,
            height=config["Cue_size"],
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

        stimuli["feedback_good"] = visual.ImageStim(
            win=win,
            image=os.path.join("input_data", "flanker_task", config["Feedback_good"]),
            size=config["Feedback_size"],
            name="feedback_good",
            interpolate=True,
        )
        stimuli["feedback_bad"] = visual.ImageStim(
            win=win,
            image=os.path.join("input_data", "flanker_task", config["Feedback_bad"]),
            size=config["Feedback_size"],
            name="feedback_bad",
            interpolate=True,
        )

    return stimuli
