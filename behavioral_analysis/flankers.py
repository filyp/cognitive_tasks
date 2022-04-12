import csv
import os
import glob
import sys

import numpy as np

print("Printng statistics for the most recent behavioral file in the given directory...")

path = sys.argv[1]
behavioral_data_glob = os.path.join(path, "behavioral_data", "*.csv")
files = glob.glob(behavioral_data_glob)
files.sort(key=os.path.getctime)
most_recent_file = files[-1]
most_recent_file


with open(most_recent_file, "r") as file:
    reader = csv.DictReader(file)
    rows = [row for row in reader]

# cluster into blocks
blocks = []
for previous_row, current_row in zip([dict()] + rows[:-1], rows):
    if previous_row.get("block_type") != current_row.get("block_type"):
        # next_row is in a new block
        blocks.append((current_row.get("block_type"), []))
    # append row to the latest block
    blocks[-1][1].append(current_row)


experiment_block = blocks[-1][1]    # TODO make it general

congruent_correct_rts = []
incongruent_correct_rts = []
congruent_error_rts = []
incongruent_error_rts = []

for row in experiment_block:
    rt = row["rt"]
    if rt == "":
        # no reaction was given
        continue
    rt = float(rt)
    if row["target_name"] in ["congruent_lll", "congruent_rrr"]:
        if row["reaction"] == "correct":
            congruent_correct_rts.append(rt)
        elif row["reaction"] == "incorrect":
            congruent_error_rts.append(rt)
        else:
            raise Exception()
    elif row["target_name"] in ["incongruent_lrl", "incongruent_rlr"]:
        if row["reaction"] == "correct":
            incongruent_correct_rts.append(rt)
        elif row["reaction"] == "incorrect":
            incongruent_error_rts.append(rt)
        else:
            raise Exception()
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


print(f"""
REACTION TIMES:
             |     CORRECT     |      ERROR      |       ALL       |
CONGRUENT    |  {stats(congruent_correct_rts)}  |  {stats(congruent_error_rts)}  |  {stats(congruent_correct_rts + congruent_error_rts)}  |
INCONGRUENT  |  {stats(incongruent_correct_rts)}  |  {stats(incongruent_error_rts)}  |  {stats(incongruent_correct_rts + incongruent_error_rts)}  |
ALL          |  {stats(congruent_correct_rts + incongruent_correct_rts)}  |  {stats(congruent_error_rts + incongruent_error_rts)}  |  {stats(congruent_correct_rts + congruent_error_rts + incongruent_correct_rts + incongruent_error_rts)}  |


NUMBER OF TRIALS:
             |     CORRECT     |      ERROR      |       ALL       |
CONGRUENT    |  {print_len(congruent_correct_rts)}  |  {print_len(congruent_error_rts)}  |  {print_len(congruent_correct_rts + congruent_error_rts)}  |
INCONGRUENT  |  {print_len(incongruent_correct_rts)}  |  {print_len(incongruent_error_rts)}  |  {print_len(incongruent_correct_rts + incongruent_error_rts)}  |
ALL          |  {print_len(congruent_correct_rts + incongruent_correct_rts)}  |  {print_len(congruent_error_rts + incongruent_error_rts)}  |  {print_len(congruent_correct_rts + congruent_error_rts + incongruent_correct_rts + incongruent_error_rts)}  |
""")


from collections import Counter

c = Counter()

for trial in experiment_block:
    rt = trial["rt"]
    feedback_type = trial["feedback_type"]
    threshold_rt = trial["threshold_rt"]
    # print(rt, feedback_type, threshold_rt)
    c.update([feedback_type])


print(c)
