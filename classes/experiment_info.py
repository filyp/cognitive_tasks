import datetime

from psychopy import gui


def get_participant_info():
    """
    okienko dialogowe na podczas uruchomienia procedury
    :return: participant_info
    """
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M")

    my_dlg = gui.Dlg(title="Participant info")
    my_dlg.addText("Informacje:")
    my_dlg.addField("ID:")
    my_dlg.addField("Wersja:", choices=["*" "A", "B"])

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)

    part_id = my_dlg.data[0]
    version = my_dlg.data[1]

    date = date.replace(":", "-")
    participant_info = "{}-{}-{}".format(part_id, version, date)
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
