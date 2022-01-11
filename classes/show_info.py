from psychopy import visual, event, logging
import time
import os

from classes.load_data import read_text_from_file
from classes.check_exit import check_exit
from classes.save_data import save_beh, save_triggers


def show_info(
    win,
    file_name,
    text_size,
    screen_width,
    insert="",
    participant_info=None,
    beh=None,
    triggers_list=None,
):
    """
    Clear way to show info message into screen.
    :param win:
    :param file_name:
    :param screen_width:
    :param text_size:
    :param insert: extra text for read_text_from_file
    :return:
    """
    hello_msg = read_text_from_file(os.path.join("messages", file_name), insert=insert)
    hello_msg = visual.TextStim(
        win=win,
        antialias=True,
        font=u"Arial",
        text=hello_msg,
        height=text_size,
        wrapWidth=screen_width,
        color=u"black",
        alignHoriz="center",
        alignVert="center",
    )
    hello_msg.draw()
    win.flip()
    key = event.waitKeys(keyList=["f7", "return", "space"])
    if key == ["f7"]:
        save_beh(beh, participant_info)
        save_triggers(triggers_list, participant_info)
        logging.critical("Experiment finished by user! {} pressed.".format(key))
        exit(1)
    win.flip()


def show_text(win, text, show_time, participant_info=None, beh=None, triggers_list=None):
    text.setAutoDraw(True)
    win.flip()
    time.sleep(show_time)
    text.setAutoDraw(False)
    check_exit(participant_info=participant_info, beh=beh, triggers_list=triggers_list)
    win.flip()
