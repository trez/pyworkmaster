import logging
import tempfile
import subprocess
import os

_log = logging.getLogger(__name__)
default_config = os.path.expanduser("~/.screenrc")


def run(config, proj):
    session = config[proj]["variables"]["PROJECT"]
    p = config[proj]

    screenrc = []

    # Get default config.
    if os.path.exists(default_config):
        with open(default_config, "r") as f:
            screenrc.extend([line.rstrip() for line in f.readlines()])

    # Create windows and set proper titles and run commands.
    screenrc.append(f"sessionname {session}")
    for num, title in enumerate(p["windows"], 1):
        screenrc.append(f"screen -t {title} {num}")
        for cmd in p["windows"][title]:
            screenrc.append(f'stuff "{cmd}^M"')

    # Create layout.
    queue = [p["layout"]]
    while queue:
        n, *queue = queue
        if not n.name.isalpha():
            num_splits = len(n.children) - 1
            split = "split -v" if n.name == "|" else "split"
            screenrc.extend([f"{split}"] * num_splits)
        else:
            screenrc.append(f"select {n.name}")
            screenrc.append("focus")
        queue.extend(n.children)
    screenrc.append("layout save default")

    # Write to temp config.
    fd, tmpfile = tempfile.mkstemp()
    with open(tmpfile, "w") as f:
        f.write("\n".join(screenrc))

    # Start screen session.
    subprocess.run(f"screen -c {tmpfile}", shell=True)
