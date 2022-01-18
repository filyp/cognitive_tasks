import time
from cmath import log

from psychopy import logging


class TriggerTypes(object):
    BLINK = "BLINK"
    CUE = "CU"
    TARGET = "TG"
    RE = "RE"
    # FEEDB_GOOD = "FG"
    # FEEDB_BAD = "FB"


def create_eeg_port():
    try:
        import parallel

        port = parallel.Parallel()
        port.setData(0x00)
        return port
    except:
        raise Exception("Can't connect to EEG")


def create_nirs_dev():
    try:
        import pyxid

        devices = pyxid.get_xid_devices()
        dev = devices[0]
        return dev
    except:
        raise Exception("Can't connect to NIRS")


class TriggerHandler:
    def __init__(self, port_eeg):
        self.port_eeg = port_eeg
        self.triggers_list = []
        self.trigger_no = 0

    def prepare_trigger(self, trigger_type, block_name, cue_name, target_name, response=None):
        self.trigger_no += 1
        if self.trigger_no == 9:
            self.trigger_no = 1

        trigger_name = (
            f"{self.trigger_no}:{trigger_type}*{block_name}*{cue_name}*{target_name}*{response}"
        )
        self.triggers_list.append(trigger_name)

    def send_trigger(self):
        logging.data("TRIGGER: " + self.triggers_list[-1])
        logging.flush()  # TODO after testing delete this to avoid potential delay
        if self.port_eeg is not None:
            try:
                self.port_eeg.setData(self.trigger_no)
                time.sleep(0.01)
                self.port_eeg.setData(0x00)
            except:
                # TODO it should at least log the error
                pass
        # if self.port_nirs is not None:
        #     try:
        #         self.port_nirs.activate_line(self.trigger_no)
        #     except:
        #         pass
