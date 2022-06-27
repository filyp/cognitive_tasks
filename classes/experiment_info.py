import datetime

from psychopy import gui


def get_participant_info(ask_for_experiment_version=False):
    """
    okienko dialogowe na podczas uruchomienia procedury
    :return: participant_info
    """
    my_dlg = gui.Dlg(title="Participant info")
    my_dlg.addText("Informacje:")
    my_dlg.addField("ID:")
    if ask_for_experiment_version:
        my_dlg.addField("Wersja:", choices=["-", "A", "B"])

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)

    part_id = my_dlg.data[0]

    if ask_for_experiment_version:
        version = my_dlg.data[1]
    else:
        version = None

    participant_info = "{}".format(part_id)
    return participant_info, version


def display_eeg_info():
    """
    Dialog info shows at the beginning of the experiment.
    """

    my_dlg = gui.Dlg(title="Reminder")
    my_dlg.addText("\n\tZanim zaczniesz zadanie, uruchom ActiView i rozpocznij zapis.")
    my_dlg.addText("")

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)
