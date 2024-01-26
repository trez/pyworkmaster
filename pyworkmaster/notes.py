import os
from datetime import datetime
from pyworkmaster.config import config


def get_note_path(project):
    wm_home = config["common"]["workmaster_home"]
    note_path = os.path.join(wm_home, f"notes-{project}")
    return note_path


def read_notes(project):
    note_path = get_note_path(project)
    if os.path.isfile(note_path):
        with open(note_path, "r") as fp:
            for line in fp.readlines():
                print(line.rstrip("\n"))


def add_note(project, note):
    note_path = get_note_path(project)
    with open(note_path, "a") as fp:
        date_str = datetime.now().strftime("%Y%m%d %H:%M")
        fp.write(f"{date_str}> {note}\n")
