import time

from psychopy import logging


# def create_eeg_port():
#     try:
#         import parallel

#         port = parallel.Parallel()
#         port.setData(0x00)
#         return port
#     except:
#         raise Exception("Can't connect to EEG")

def create_eeg_port():
    try:
        import serial

        port = serial.Serial("/dev/ttyUSB0", baudrate=115200)
        port.write(0x00)
        return port
    except:
        raise Exception("Can't connect to EEG")


def simple_send_trigger(port_eeg, trigger_no):
    port_eeg.write(trigger_no.to_bytes(1, 'big'))
    time.sleep(0.005)
    port_eeg.write(0x00)
    time.sleep(0.005)


class TriggerHandler:
    def __init__(self, port_eeg, data_saver):
        self.port_eeg = port_eeg
        self.data_saver = data_saver
        self.trigger_no = 1
        self.trial = None

    def prepare_trigger(self, trigger_name):
        self.trigger_no *= 2
        if self.trigger_no == 256:
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
                simple_send_trigger(self.port_eeg, self.trigger_no)
            except Exception as ex:
                logging.error(ex)

    def open_trial(self):
        self.trial = []

    def close_trial(self, value):
        for trig in self.trial:
            trig = trig.format(value)
            self.data_saver.triggers_list.append(trig)
        self.trial = None