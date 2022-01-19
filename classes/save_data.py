import csv
import os

from psychopy import event, logging


class DataSaver:
    def __init__(self, participant_info, beh=[], triggers_list=[]):
        self.participant_info = participant_info
        self.beh = beh
        self.triggers_list = triggers_list

    def save_triggers(self):
        path = os.path.join(
            "results", "triggers_maps", "triggerMap_{}.txt".format(self.participant_info)
        )
        with open(path, "w") as map_file:
            map_file.write("\n".join(self.triggers_list))

    def save_beh(self):
        path = os.path.join(
            "results", "behavioral_data", "beh_{}.csv".format(self.participant_info)
        )
        with open(path, "w") as csvfile:
            fieldnames = [
                "block type",
                "trial type",
                "cue name",
                "target name",
                "response",
                "rt",
                "reaction",
                "cal mean rt",
                "cutoff",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.beh:
                writer.writerow(row)

    def check_exit(self, key="f7"):
        stop = event.getKeys(keyList=[key])
        if len(stop) > 0:
            self.save_beh()
            self.save_triggers()
            logging.critical("Experiment finished by user! {} pressed.".format(key))
            exit(1)
