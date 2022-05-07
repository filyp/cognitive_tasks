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
    stimuli = dict()

    for stimulus_name, stimulus_definition in config["Stimuli"].items():
        path, size = stimulus_definition
        stimuli[stimulus_name] = visual.ImageStim(
            win=win,
            image=os.path.join("input_data", "monetary_incentive_delay", path),
            size=size,
            name=stimulus_name,
            interpolate=True,
        )

    return stimuli
