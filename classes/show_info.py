import os

from psychopy import event, logging, visual

from classes.load_data import read_text_from_file


class TriggerTypes:
    BLOCK_START = "BLOCK_START"


def show_info(
    win,
    file_name,
    config,
    screen_width,
    data_saver,
    trigger_handler,
    insert="",
):
    """
    Clear way to show info message into screen.
    :param win:
    :param file_name:
    :param screen_width:
    :param text_size:
    :param text_color:
    :param insert: extra text for read_text_from_file
    :return:
    """
    hello_msg = read_text_from_file(os.path.join("messages", file_name), insert=insert)
    hello_msg = visual.TextStim(
        win=win,
        antialias=True,
        font=config["Text_font"],
        text=hello_msg,
        height=config["Text_size"],
        wrapWidth=screen_width,
        color=config["Text_color"],
    )
    hello_msg.draw()
    win.flip()
    key = event.waitKeys(keyList=["f7", "return", "space"])
    if key == ["f7"]:
        data_saver.save_beh()
        data_saver.save_triggers()
        logging.critical("Experiment finished by user! {} pressed.".format(key))
        exit(1)

    trigger_handler.prepare_trigger(trigger_type=TriggerTypes.BLOCK_START)
    trigger_handler.send_trigger()
    win.flip()
