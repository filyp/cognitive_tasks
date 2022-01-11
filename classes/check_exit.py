from psychopy import event, logging
from classes.save_data import save_beh, save_triggers


def check_exit(key="f7", part_id="", beh=None, triggers_list=None):
    stop = event.getKeys(keyList=[key])
    if len(stop) > 0:
        save_beh(beh, part_id)
        save_triggers(triggers_list, part_id)
        logging.critical("Experiment finished by user! {} pressed.".format(key))
        exit(1)
