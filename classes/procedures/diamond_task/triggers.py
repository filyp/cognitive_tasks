import time

from psychopy import logging


class TriggerTypes:
    EXPERIMENT_START = "EXPERIMENT_START"
    BLOCK_START = "BLOCK_START"
    IMAGE = "IMAGE___"
    CHOICE_PROMPT = "CHOICE_P"
    CUES = [
        "CUE_1___",
        "CUE_2___",
        "CUE_3___",
        "CUE_4___",
        "CUE_5___",
        "CUE_6___",
    ]
    FEEDB_GOOD = "F_GOOD__"
    FEEDB_BAD = "F_BAD___"


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
    def __init__(self, port_eeg, data_saver):
        self.port_eeg = port_eeg
        self.data_saver = data_saver
        self.trigger_no = 0

    def prepare_trigger(
        self,
        trigger_type,
        block_type="--",
    ):
        self.trigger_no += 1
        if self.trigger_no == 9:
            self.trigger_no = 1

        trigger_name = f"{self.trigger_no}:{trigger_type}*{block_type[:2]}"
        self.data_saver.triggers_list.append(trigger_name)

    def send_trigger(self):
        logging.data("TRIGGER: " + self.data_saver.triggers_list[-1])
        if self.port_eeg is not None:
            try:
                self.port_eeg.setData(self.trigger_no)
                time.sleep(0.01)
                self.port_eeg.setData(0x00)
            except Exception as ex:
                logging.error(ex)
                pass
        # if self.port_nirs is not None:
        #     try:
        #         self.port_nirs.activate_line(self.trigger_no)
        #     except Exception as ex:
        #         logging.error(ex)
        #         pass
