import os

from psychopy import logging, visual

from classes.load_data import read_text_from_file
from classes.triggers import TriggerTypes

# TODO this file is outdated - it has to be modified to use TriggerHandler


def ophthalmic_procedure(
    win,
    screen_res,
    frames_per_sec,
    trigger_no,
    triggers_list,
    text_size,
    text_color,
    send_eeg_triggers=False,
    send_nirs_triggers=False,
    port_eeg=None,
    port_nirs=None,
    vis_offset=60,
    secs_of_msg=5,
    secs_of_blinks=9,
    secs_of_saccades=9,
    data_saver=None,
):
    """
    :param port_nirs:
    :param port_eeg:
    :param send_nirs_triggers:
    :param text_size:
    :param text_color:
    :param triggers_list:
    :param trigger_no:
    :param frames_per_sec:
    :param screen_res:
    :param win:
    :param send_eeg_triggers:
    :param vis_offset: No of pixels of margin between fixation crosses and screen border
    :param secs_of_msg:
    :param secs_of_blinks:
    :param secs_of_saccades:
    :param data_saver:
    :return:
    """
    logging.info("Starting ophthalmic procedure... ")
    # prepare stim's
    ophthalmic_info = read_text_from_file(
        os.path.join(".", "messages", "ophthalmic_instruction.txt")
    )
    corners_info = read_text_from_file(os.path.join(".", "messages", "ophthalmic_corners.txt"))

    ophthalmic_info = visual.TextStim(
        win=win,
        font="Arial",
        text=ophthalmic_info,
        height=text_size,
        wrapWidth=screen_res["width"],
        color=text_color,
    )
    corners_info = visual.TextStim(
        win=win,
        font="Arial",
        text=corners_info,
        height=text_size,
        wrapWidth=screen_res["width"],
        color=text_color,
    )
    # crosses are located in corners
    crosses = [
        [x, y]
        for x in [
            -screen_res["width"] / 2 + vis_offset,
            screen_res["width"] / 2 - vis_offset,
        ]
        for y in [
            -screen_res["height"] / 2 + vis_offset,
            screen_res["height"] / 2 - vis_offset,
        ]
    ]
    crosses = [
        visual.TextStim(win=win, text="+", height=3 * text_size, color=text_color, pos=pos)
        for pos in crosses
    ]

    ophthalmic_info.setAutoDraw(True)
    for _ in range(frames_per_sec * secs_of_msg):
        win.flip()
        data_saver.check_exit()
    ophthalmic_info.setAutoDraw(False)
    win.flip()

    for frame_counter in range(frames_per_sec * secs_of_blinks):
        if frame_counter % frames_per_sec == 0:
            trigger_no, triggers_list = prepare_trigger(
                trigger_type=TriggerTypes.BLINK,
                trigger_no=trigger_no,
                triggers_list=triggers_list,
            )
            send_trigger(
                port_eeg=port_eeg,
                port_nirs=port_nirs,
                trigger_no=trigger_no,
                send_eeg_triggers=send_eeg_triggers,
                send_nirs_triggers=send_nirs_triggers,
            )
        win.flip()
        data_saver.check_exit()

    corners_info.setAutoDraw(True)
    for _ in range(frames_per_sec * secs_of_msg):
        win.flip()
        data_saver.check_exit()
    corners_info.setAutoDraw(False)

    [item.setAutoDraw(True) for item in crosses]
    for frame_counter in range(frames_per_sec * secs_of_saccades):
        if frame_counter % frames_per_sec == 0:
            trigger_no, triggers_list = prepare_trigger(
                trigger_type=TriggerTypes.BLINK,
                trigger_no=trigger_no,
                triggers_list=triggers_list,
            )
            send_trigger(
                port_eeg=port_eeg,
                port_nirs=port_nirs,
                trigger_no=trigger_no,
                send_eeg_triggers=send_eeg_triggers,
                send_nirs_triggers=send_nirs_triggers,
            )
        win.flip()
        data_saver.check_exit()
    [item.setAutoDraw(False) for item in crosses]
    win.flip()

    logging.info("Ophthalmic procedure finished correctly!")

    return trigger_no, triggers_list
