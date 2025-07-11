import os
import codecs

from psychopy import event, logging, visual



def show_text(
    text,
    win,
    data_saver,
    **text_stim_kwargs,
):
    visual.TextStim(
        text=text,
        win=win,
        **text_stim_kwargs,
    ).draw()
    win.flip()
    key = event.waitKeys(keyList=["f7", "space"])
    if key == ["f7"]:
        data_saver.terminate_early()


# ! the rest of the file is deprecated but needed for old procedures
# ! for new ones, just use the show_text function above


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
                msg.append(line)
    whole_message = "".join(msg)
    final_message = whole_message.replace("<--insert-->", insert)
    return final_message

# for more functionality, you can also adopt: https://github.com/filyp/psychopy_experiment_helpers/blob/355e71cade005eedeb1186274ba819f91e561179/show_info.py
def show_info(
    win,
    file_name,
    config,
    screen_width=None,
    data_saver=None,
    insert="",
    alignText="center",
    pos=(0, 0),
    insert_dict={},
):
    # note: using insert is deprecated - better to use insert_dict
    hello_msg = read_text_from_file(os.path.join("messages", file_name), insert=insert)
    hello_msg = hello_msg.format(**insert_dict)
    hello_msg = visual.TextStim(
        win=win,
        antialias=True,
        font=config["Text_font"],
        text=hello_msg,
        height=config["Text_size"],
        wrapWidth=screen_width,
        color=config["Text_color"],
        alignText=alignText,
        pos=pos,
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
