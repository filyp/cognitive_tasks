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
    my_dlg.addField("Wiek:")
    my_dlg.addField("Plec:", choices=["Mezczyzna", "Kobieta"])
    my_dlg.addField("Wersja:", choices=["-", "A", "B"])

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)

    part_id = my_dlg.data[0]
    age = my_dlg.data[1]
    sex = my_dlg.data[2]
    version = my_dlg.data[3]

    date = date.replace(":", "-")
    participant_info = "{}_{}_{}_{}_{}".format(part_id, sex, age, version, date)
    return participant_info, version


def display_eeg_info():
    """
    Dialog info shows at the beginning of the experiment.
    """

    my_dlg = gui.Dlg(title="Reminder")
    my_dlg.addText("\n\tUruchom ActiView zanim zaczniesz zadanie.")
    my_dlg.addText("")

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)
