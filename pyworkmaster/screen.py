import logging
import tempfile
import subprocess
import os

_log = logging.getLogger(__name__)
default_config = os.path.expanduser("~/.screenrc")


def setup(p):
    screenrc = []

    # Get default config.
    if os.path.exists(default_config):
        with open(default_config, "r") as f:
            screenrc.extend([line.rstrip() for line in f.readlines()])

    # Create windows and set proper titles and run commands.
    screenrc.append(f"sessionname {p['variables']['PROJECT']}")
    for num, title in enumerate(p["windows"], 1):
        screenrc.append(f"screen -t {title} {num}")
        for cmd in p["windows"][title]:
            screenrc.append(f'stuff "{cmd}^M"')

    # Create layout.
    screenrc.append(f"# layout: {p['layout']}")
    queue = [p["layout"]]
    while queue:
        n, *queue = queue
        queue = n.children + queue
        if not n.name.isalpha():
            num_splits = len(n.children) - 1
            split = "split -v" if n.name == "|" else "split"
            screenrc.extend([f"{split}"] * num_splits)
        else:
            screenrc.append(f"select {n.name}")
            screenrc.append("focus")
    screenrc.append("layout save default")
    screenrc.append("detach")

    # Write to temp config.
    screenrc.append("")
    fd, tmpfile = tempfile.mkstemp()
    with open(tmpfile, "w") as f:
        f.write("\n".join(screenrc))

    # Start screen session.
    process = subprocess.run(
        f"screen -c {tmpfile}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return process.returncode


def attach(p):
    subprocess.run(f"screen -x {p}", shell=True)


def is_setup(p):
    process = subprocess.run(
        f"screen -S {p} -Q select .",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return process.returncode == 0


def kill(p):
    subprocess.run(f"screen -XS {p} quit", shell=True)


def run_command(session, window, cmd):
    subprocess.run(f"screen -S {session} -p {window} -X stuff '{cmd}^M'", shell=True)
