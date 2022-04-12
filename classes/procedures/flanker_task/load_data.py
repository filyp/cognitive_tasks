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

    if "Right_char" in config:
        # specify flankers by UNICODE chars

        # ! create fixation
        stimuli["fixation"] = visual.TextStim(
            win,
            color=config["Text_color"],
            text=config["Fixation_char"],
            font=config["Flanker_font"],
            height=config["Flanker_size"],
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
            stim = visual.TextStim(
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
            stimuli[stimulus_name] = [
                stim
            ]  # use a list to be interchangable with the image loading code
    else:
        # create flankers by images
        # ! create fixation
        stimuli["fixation"] = visual.ImageStim(
            win=win,
            image=os.path.join("input_data", "flanker_task", "fixation.png"),
            size=config["Flanker_size"],
            name="fixation",
        )

        # ! create targets and flankers
        left_ = []
        right = []
        for i in range(5):
            name = "left" + str(i)
            left_.append(
                visual.ImageStim(
                    win=win,
                    image=os.path.join("input_data", "flanker_task", "arrow_left.png"),
                    size=config["Flanker_size"],
                    pos=(0, (i - 2) * config["Flanker_spacing"]),
                    name=name,
                )
            )
            name = "right" + str(i)
            right.append(
                visual.ImageStim(
                    win=win,
                    image=os.path.join("input_data", "flanker_task", "arrow_right.png"),
                    size=config["Flanker_size"],
                    pos=(0, (i - 2) * config["Flanker_spacing"]),
                    name=name,
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
        pos_x, pos_y = config["Feedback_position"]
        abs_feedback_position = (
            pos_x * config["Feedback_size"],
            pos_y * config["Feedback_size"],
        )
        stimuli["feedback_good"] = visual.TextStim(
            win,
            color=config["Text_color"],
            text=config["Feedback_good"],
            font=config["Feedback_font"],
            height=config["Feedback_size"],
            name="feedback_good",
            pos=abs_feedback_position,
        )
        stimuli["feedback_bad"] = visual.TextStim(
            win,
            color=config["Text_color"],
            text=config["Feedback_bad"],
            font=config["Feedback_font"],
            height=config["Feedback_size"],
            name="feedback_bad",
            pos=abs_feedback_position,
        )

    return stimuli
