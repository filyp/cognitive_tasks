import os
from psychopy import visual

possible_images_format = ("bmp", "jpg", "png", "gif", "webp")
possible_audio_format = ("mp3", "au", "mp2", "wav", "wma", "ogg")


def load_stimuli(win, config, screen_res):
    """
    ladowanie tekstu, zdjec i dzwiekow
    :param screen_res:
    :param config:
    :param win: visual.Window z psychopy
    :param folder_name: nazwa folderu z ktorego beda ladowane pliki
    """

    stimuli = dict()

    # ! create fixation
    stimuli["fixation"] = visual.TextStim(
        win,
        text="+",
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Text_size"],
        name="fixation",
    )

    size = config["Arrows_size"]
    arrow_offset = size * 0.7

    # ! create arrows
    stimuli["right_arrow"] = visual.ImageStim(
        win,
        image=os.path.join("input_data", "diamond_task", "right_arrow.png"),
        size=size,
        ori=0,
        pos=(arrow_offset, 0),
        name="right_arrow",
    )
    stimuli["left_arrow"] = visual.ImageStim(
        win,
        image=os.path.join("input_data", "diamond_task", "right_arrow.png"),
        size=size,
        ori=180,
        pos=(-arrow_offset, 0),
        name="left_arrow",
    )
    stimuli["down_arrow"] = visual.ImageStim(
        win,
        image=os.path.join("input_data", "diamond_task", "right_arrow.png"),
        size=size,
        ori=90,
        pos=(0, -arrow_offset),
        name="down_arrow",
    )

    square_offset_x = size * 0.7
    square_offset_y = size * 0.8

    stimuli["left_square"] = visual.ImageStim(
        win,
        image=os.path.join("input_data", "diamond_task", "square.webp"),
        size=size * 0.8,
        pos=(-square_offset_x, square_offset_y),
        name="left_square",
    )
    stimuli["right_square"] = visual.ImageStim(
        win,
        image=os.path.join("input_data", "diamond_task", "square.webp"),
        size=size * 0.8,
        pos=(square_offset_x, square_offset_y),
        name="right_square",
    )

    stimuli["left_text"] = visual.TextStim(
        win,
        text="A",
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Info_size"],
        pos=(-square_offset_x, square_offset_y),
        name="left_text",
    )
    stimuli["right_text"] = visual.TextStim(
        win,
        text="B",
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Info_size"],
        pos=(square_offset_x, square_offset_y),
        name="right_text",
    )
    stimuli["middle_text"] = visual.TextStim(
        win,
        text="",
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Info_size"],
        name="middle_text",
        wrapWidth=screen_res["width"],
    )

    stimuli["top_text"] = visual.TextStim(
        win,
        text="",
        pos=(0, 0.2),
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Text_size"],
        name="top_text",
        wrapWidth=screen_res["width"],
    )

    stimuli["feedback_good"] = visual.TextStim(
        win,
        text=config["Feedback_good"],
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Text_size"],
        name="feedback_good",
        wrapWidth=screen_res["width"],
    )
    stimuli["feedback_bad"] = visual.TextStim(
        win,
        text=config["Feedback_bad"],
        color=config["Text_color"],
        font=config["Text_font"],
        height=config["Text_size"],
        name="feedback_bad",
        wrapWidth=screen_res["width"],
    )

    return stimuli
