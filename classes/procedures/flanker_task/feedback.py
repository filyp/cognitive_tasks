import numpy as np
from psychopy import logging

from classes.procedures.flanker_task.triggers import TriggerTypes


class FeedbackTimerSteps:
    """
    This feedback timer aims to achieve some set error rate.
    Error rate is the ratio of errors on incongruent trials, to all incongruent trials.
    Here it is aimed at 20%.

    Note that people often ignore positive feedback, focusing on accuracy,
    so the thresholds can get large.
    """

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


class FeedbackTimerMovingMedian:
    def __init__(self, initial_threshold_rt, timer_names):
        self.RTs = dict()
        self.thresholds = dict()
        for name in timer_names:
            name = str(name)
            self.RTs[name] = [initial_threshold_rt]
            self.thresholds[name] = initial_threshold_rt

        self.percent_of_positive_feedback = 50
        self.num_of_trials = 20

    def update_threshold(self, target_name, reaction, timer_name):
        # no need to update anything here, because it's called for each trial
        # but we care only for correct ones
        pass

    def get_feedback(self, reaction_time, timer_name):
        # use only RTs for this cue
        latest_RTs = self.RTs[timer_name][-self.num_of_trials :]

        # update RTs
        self.RTs[timer_name].append(reaction_time)

        self.thresholds[timer_name] = np.percentile(latest_RTs, self.percent_of_positive_feedback)
        logging.data(f"threshold for {timer_name} at {self.thresholds[timer_name]:.3f} ms")

        if reaction_time < self.thresholds[timer_name]:
            return "feedback_good", TriggerTypes.FEEDB_GOOD
        else:
            return "feedback_bad", TriggerTypes.FEEDB_BAD
