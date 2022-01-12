from collections import OrderedDict

from psychopy import event, logging, visual


def get_screen_res():
    """
    Funcion that check current screen resolution. Raise OSError if can't recognise OS!
    * :return: (width, height) tuple with screen resolution.
    """
    import platform

    system = platform.system()
    if "Linux" in system:
        import re
        import subprocess

        output = subprocess.Popen(
            'xrandr | grep "\*" | cut -d" " -f4', shell=True, stdout=subprocess.PIPE
        )
        output = output.communicate()[0]
        output = output.decode()
        # in case of multiple screens, use the primary one
        output = output.splitlines()[0]

        valid_res = lambda x: re.match("^\d{3,4}x\d{3,4}$", x)
        if not valid_res(output):
            output = subprocess.Popen(
                ' xdpyinfo | grep dimensions | cut -d" " -f7',
                shell=True,
                stdout=subprocess.PIPE,
            )
            output = output.communicate()[0]
            output = output.decode()
        if not valid_res(output):
            logging.ERROR("OS ERROR - no way of determine screen res")
            raise OSError(
                "Humanity need more time to come up with efficient way of checking screen resolution of your hamster"
            )
        width, height = map(int, output.split("x"))
    elif "Windows" in system:
        from win32api import GetSystemMetrics

        width = int(GetSystemMetrics(0))
        height = int(GetSystemMetrics(1))
    else:  # can't recognise OS
        logging.ERROR("OS ERROR - no way of determine screen res")
        raise OSError("get_screen_res function can't recognise your OS")
    logging.info("Screen res set as: {}x{}".format(width, height))

    return OrderedDict(width=width, height=height)


def get_frame_rate(win, legal_frame_rates=(60, 30)):
    frame_rate = 30  # int(round(win.getActualFrameRate(nIdentical=30, nMaxFrames=200)))
    logging.info("Detected framerate: {} frames per sec.".format(frame_rate))
    assert frame_rate in legal_frame_rates, "Illegal frame rate."
    return frame_rate


def create_win(screen_color):
    """
    zwraca ekran na ktorym bedzie wszystko wyswietlane
    wylacza myszke
    :param screen_color: kolor tla
    :return: zwraca ekran na ktorym bedzie wszystko wyswietlane
    """
    screen_res = get_screen_res()
    screen_res_list = list(screen_res.values())
    win = visual.Window(
        screen_res_list,
        fullscr=True,
        monitor="TestMonitor",  # todo? this may be invalid argument value
        units="pix",
        screen=0,
        color=screen_color,
    )
    event.Mouse(visible=False, newPos=None, win=win)
    win.flip()
    frames_per_sec = get_frame_rate(win=win)
    return win, screen_res, frames_per_sec
