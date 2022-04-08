import os
import codecs

from psychopy import event, logging, visual


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


def show_info(
    win,
    file_name,
    config,
    screen_width,
    data_saver,
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

    win.flip()
