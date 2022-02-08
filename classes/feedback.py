from psychopy import logging

from classes.triggers import TriggerTypes


class FeedbackTimer:
    def __init__(self, initial_threshold_rt, timer_names):
        self.thresholds = dict()
        for name in timer_names:
            name = str(name)
            self.thresholds[name] = initial_threshold_rt

    def update_threshold(self, target_name, reaction, timer_name):
        if target_name not in ["incongruent_rlr", "incongruent_lrl"]:
            # we update only during incongruent trials
            return

        if reaction == "correct":
            update = -0.005
            # TODO calculate those updates based on configurable arguments
        elif reaction == "incorrect":
            update = 0.020

        self.thresholds[timer_name] += update
        logging.data(f"updated threshold for timer={timer_name} to {self.thresholds[timer_name]}")

    def get_feedback(self, reaction_time, timer_name):
        if reaction_time < self.thresholds[timer_name]:
            return "feedback_good", TriggerTypes.FEEDB_GOOD
        else:
            return "feedback_bad", TriggerTypes.FEEDB_BAD
