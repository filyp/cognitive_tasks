import csv
import os

from psychopy import event, logging


class DataSaver:
    def __init__(self, participant_info, experiment_name, beh=[], triggers_list=[]):
        self.participant_info = participant_info
        self.experiment_name = experiment_name
        self.beh = beh
        self.triggers_list = triggers_list
        self.directory = os.path.join("results", self.experiment_name)

    def save_triggers(self):
        trigger_directory = os.path.join(self.directory, "triggers_maps")
        os.makedirs(trigger_directory, exist_ok=True)
        filename = "triggerMap_{}.txt".format(self.participant_info)
        path = os.path.join(trigger_directory, filename)
        with open(path, "w") as map_file:
            lines = ((trigger + "\r\n") for trigger in self.triggers_list)
            map_file.writelines(lines)

    def save_beh(self):
        behavioral_directory = os.path.join(self.directory, "behavioral_data")
        os.makedirs(behavioral_directory, exist_ok=True)
        filename = "beh_{}.csv".format(self.participant_info)
        path = os.path.join(behavioral_directory, filename)
        # assumes that the first row already contains all the fields (there are no fields left out)
        if self.beh == []:
            return  # nothing to save
        fieldnames = list(self.beh[0].keys())
        with open(path, "w") as csvfile:
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
