
import csv
import os
import glob
import sys

import numpy as np

print("Printng statistics for the most recent behavioral file in the given directory...")
print("Statistics based on all the trials apart from training trials.")

path = sys.argv[1]
behavioral_data_glob = os.path.join(path, "behavioral_data", "*.csv")
files = glob.glob(behavioral_data_glob)
files.sort(key=os.path.getctime)
most_recent_file = files[-1]


with open(most_recent_file, "r") as file:
    reader = csv.DictReader(file)
    rows = [row for row in reader]

experiment_rows = [row for row in rows if row["block_type"]=="experiment"]


num_of_positive_feedback = 0
num_of_negative_feedback = 0
RTs_in_positive = []
RTs_in_negative = []
RTs_in_neutral = []

for row in experiment_rows:
    feedback_type = row["feedback_type"]
    if feedback_type == "feedback_good":
        num_of_positive_feedback += 1
    elif feedback_type == "feedback_bad":
        num_of_negative_feedback += 1

    rt = row["reaction_time"]
    if rt == "":
        # no reaction was given
        continue
    rt = float(rt)

    if feedback_type == "feedback_good":
        RTs_in_positive.append(rt)
    elif feedback_type == "feedback_bad":
        RTs_in_negative.append(rt)
    elif feedback_type == "feedback_neutral":
        RTs_in_neutral.append(rt)
    else:
        raise Exception()


def stats(data):
    if len(data) < 2:
        return "      -      "
    mean = np.mean(data)
    # use ddof=1 to calculate sample std, not population std
    standard_error = np.std(data, ddof=1) / np.sqrt(len(data))
    return f"{mean:.3f} ± {standard_error:.3f}"


def print_len(data):
    return f"{len(data):8d}     "


anticipation_times = [row["premature_reaction_time_since_cue_offset"] for row in experiment_rows]
anticipation_times = [float(rt) for rt in anticipation_times if rt != ""]
anticipation_times = [rt for rt in anticipation_times if rt > 1]

print(f"""
REACTION TIMES:
positive feedback        = {stats(RTs_in_positive)}
negative feedback        = {stats(RTs_in_negative)}
all incentivised trials  = {stats(RTs_in_positive+RTs_in_negative)}
neutral trials           = {stats(RTs_in_neutral)}

NUMBER OF TRIALS:
positive feedback = {num_of_positive_feedback} 
negative feedback = {num_of_negative_feedback} 
percent of positive feedback = {num_of_positive_feedback / (num_of_positive_feedback + num_of_negative_feedback) * 100:.0f} %

all trials = {len(experiment_rows)}
trials with premature reaction = {len(anticipation_times)}       (reactions >1s after cue offset, but before target)
"""
)