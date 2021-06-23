import logging
import tempfile
import subprocess
import os

_log = logging.getLogger(__name__)


def run(config, proj):
    session = config[proj]['variables']['PROJECT']
    p = config[proj]

    screenrc = []

    # Get default config.
    with open(os.path.expanduser("~/.screenrc"), "r") as f:
        screenrc.extend([l.rstrip() for l in f.readlines()])

    # Create windows and set proper titles and run commands.
    screenrc.append(f"sessionname {session}")
    for num, title in enumerate(p['windows'], 1):
        screenrc.append(f"screen -t {title} {num}")
        for cmd in p['windows'][title]:
            screenrc.append(f"stuff \"{cmd}^M\"")

    # Create layout.
    queue = [p['layout']]
    while queue:
        n = queue[0]
        queue = queue[1:]
        if not n.name.isalpha():
            num_splits = len(n.children)-1
            screenrc.extend([f"split{' -v' if n.name == '|' else ''}"]*num_splits)
        else:
            screenrc.append(f"select {n.name}")
            screenrc.append("focus")
        queue.extend(n.children)
    screenrc.append("layout save default")

    # Write to temp config.
    fd, tmpfile = tempfile.mkstemp()
    with open(tmpfile, "w") as f:
        for line in screenrc:
            f.write(f"{line}\n")

    # Start screen session.
    subprocess.run(f"screen -c {tmpfile}", shell=True)
