import os
import time

from psychopy import core, event, logging, visual

from classes.load_data import load_data
from classes.procedures.go_no_go.prepare_experiment import prepare_trials
from classes.procedures.go_no_go.triggers import (
    TriggerTypes,
    create_eeg_port,
    prepare_trigger,
    prepare_trigger_name,
    send_trigger,
)
from classes.show_info import show_info


def topological_task(
    win,
    screen_res,
    config,
    data_saver,
):
    # Load stimulus images
    stimulus = load_data(win=win, folder_name=os.path.join("input_data", "topological_task"), config=config, screen_res=screen_res)
    stimulus_dict = {stim["name"]: stim for stim in stimulus}

    frame_rate = int(round(win.getActualFrameRate()))
    logging.data(f"Frame rate: {frame_rate}")
    assert frame_rate in [24, 25, 30, 50, 60, 74, 75, 100, 120, 144, 200, 240, 360], "Illegal frame rate."
    frame_time = 1 / frame_rate

    # EEG triggers
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    triggers_list = list()
    trigger_no = 0
    data_saver.triggers_list = triggers_list

    fixation = visual.TextStim(
        win, color="black", text="+", height=2 * config["Fix_size"], pos=(0, 0.006)
    )
    
    # Response options
    response_yes = visual.TextStim(
        win, color="black", text="yes", height=config["Response_text_size"], 
        pos=(0, -config["Response_text_offset"])
    )
    response_no = visual.TextStim(
        win, color="black", text="no", height=config["Response_text_size"], 
        pos=(0, -config["Response_text_offset"] - config["Response_text_spacing"])
    )
    
    clock = core.Clock()

    # Example of one trial - you'll need to loop through actual trials
    trial_example = {
        "image": stimulus_dict["example_image"],  # Replace with actual image
        "label": "NA",  # or "W"
        "image_name": "example_image",
        "expected_response": "yes"  # or "no"
    }
    
    # Run one trial
    run_topological_trial(
        win=win,
        trial=trial_example,
        fixation=fixation,
        response_yes=response_yes,
        response_no=response_no,
        clock=clock,
        config=config,
        data_saver=data_saver,
        frame_time=frame_time
    )

    return


def run_topological_trial(win, trial, fixation, response_yes, response_no, clock, config, data_saver, frame_time):
    """
    Run one trial of the topological task following the EEG study procedure.
    """
    reaction_time = None
    response = None
    
    # 1. Text prompt for 2 seconds
    # Create prompt text with image name substitution
    prompt_text = config["Prompt_text"].replace("X", trial["image_name"])
    prompt_stimulus = visual.TextStim(
        win, color="black", text=prompt_text, height=config["Prompt_text_size"], 
        pos=(0, 0), wrapWidth=config["Prompt_wrap_width"]
    )
    
    prompt_stimulus.setAutoDraw(True)
    win.flip()
    time.sleep(config["Prompt_show_time"])
    prompt_stimulus.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()
    
    # 2. Fixation cross for 800 ms
    fixation.setAutoDraw(True)
    win.flip()
    time.sleep(config["Fixation_before_image_time"])
    fixation.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()
    
    # 3. Image for 3 seconds
    trial["image"]["stimulus"].setAutoDraw(True)
    win.flip()
    time.sleep(config["Image_show_time"])
    trial["image"]["stimulus"].setAutoDraw(False)
    data_saver.check_exit()
    win.flip()
    
    # 4. Fixation cross for 800 ms
    fixation.setAutoDraw(True)
    win.flip()
    time.sleep(config["Fixation_before_label_time"])
    fixation.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()
    
    # 5. NA or W for 1000 ms (no responses allowed)
    label_stimulus = visual.TextStim(
        win, color="black", text=trial["label"], height=config["Label_text_size"], 
        pos=(0, 0)
    )
    label_stimulus.setAutoDraw(True)
    win.flip()
    
    # Clear any existing key presses
    event.clearEvents()
    
    # Wait for 1000ms with no responses allowed
    time.sleep(config["Label_no_response_time"])
    data_saver.check_exit()
    
    # 6. Response options appear below NA or W for 3 seconds or until response
    response_yes.setAutoDraw(True)
    response_no.setAutoDraw(True)
    win.callOnFlip(clock.reset)
    win.flip()
    
    # Collect response
    response_collected = False
    response_keys = config["Response_keys"]  # ["lctrl", "rctrl"]
    
    while clock.getTime() < config["Response_window_time"] and not response_collected:
        keys = event.getKeys(keyList=response_keys, timeStamped=clock)
        if keys:
            key_pressed, reaction_time = keys[0]
            response_collected = True
            
            # Map key to response based on participant's key mapping
            if key_pressed == config["Yes_key"]:
                response = "yes"
            elif key_pressed == config["No_key"]:
                response = "no"
            
            break
        
        data_saver.check_exit()
        win.flip()
    
    # Clear stimuli
    label_stimulus.setAutoDraw(False)
    response_yes.setAutoDraw(False)
    response_no.setAutoDraw(False)
    win.flip()
    
    # 7. Fixation cross for 800 ms before next trial
    fixation.setAutoDraw(True)
    win.flip()
    time.sleep(config["Fixation_end_trial_time"])
    fixation.setAutoDraw(False)
    data_saver.check_exit()
    win.flip()
    
    # For now, just log the trial results (you can expand this later)
    print(f"Trial completed: Image={trial['image_name']}, Label={trial['label']}, Response={response}, RT={reaction_time}")
    
    return {
        "image_name": trial["image_name"],
        "label": trial["label"],
        "response": response,
        "reaction_time": reaction_time,
        "expected_response": trial["expected_response"]
    }
