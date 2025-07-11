import time

from psychopy import logging


def create_eeg_port():
    try:
        import parallel

        port = parallel.Parallel()
        port.setData(0x00)
        return port
    except:
        raise Exception("Can't connect to EEG")


class TriggerHandler:
    def __init__(self, port_eeg, data_saver):
        self.port_eeg = port_eeg
        self.data_saver = data_saver
        self.trigger_no = 0
        self.trial = None

    def prepare_trigger(self, trigger_name):
        self.trigger_no += 1
        if self.trigger_no == 9:
            self.trigger_no = 1
        line = f"{self.trigger_no}:{trigger_name}"
        if self.trial is not None:
            self.trial.append(line)
        else:
            self.data_saver.triggers_list.append(line)

    def send_trigger(self):
        # if self.trial is not None:
            # logging.data("TRIGGER: " + self.trial[-1])
            # logging.flush()
        if self.port_eeg is not None:
            try:
                self.port_eeg.setData(self.trigger_no)
                time.sleep(0.005)
                self.port_eeg.setData(0x00)
                time.sleep(0.005)
            except Exception as ex:
                logging.error(ex)

    def open_trial(self):
        self.trial = []

    def close_trial(self, value):
        for trig in self.trial:
            trig = trig.format(value)
            self.data_saver.triggers_list.append(trig)
        self.trial = None