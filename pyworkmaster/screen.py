import logging
import tempfile
import subprocess
import os

_log = logging.getLogger(__name__)
default_config = os.path.expanduser("~/.screenrc")


def setup(p):
    # Create screenrc
    screenrc = _create_screenrc(
        p['variables']['PROJECT'],
        p['windows'],
        p['layouts'],
    )

    # Write to temp config.
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


def _create_screenrc(name, windows, layouts):
    screenrc = []

    # Get default config.
    if os.path.exists(default_config):
        with open(default_config, "r") as f:
            screenrc.extend([line.rstrip() for line in f.readlines()])

    # Create windows and set proper titles and run commands.
    screenrc.append(f"sessionname {name}")
    for num, title in enumerate(windows, 1):
        screenrc.append(f"screen -t {title} {num}")
        for cmd in windows[title]:
            screenrc.append(f'stuff "{cmd}^M"')

    # Create layout.
    screenrc.append(f"# layout: {layouts}")
    for layout_name, layout in layouts.items():
        screenrc.append(f"layout new {layout_name}")
        queue = [layout]
        while queue:
            n, *queue = queue
            queue = _calc_size(n.children) + queue

            if n.size:
                screenrc.append(f"resize {n.size}%")

            if not n.name.isalpha():
                num_splits = len(n.children) - 1
                split = "split -v" if n.name == "|" else "split"
                screenrc.extend([f"{split}"] * num_splits)
            else:
                screenrc.append(f"select {n.name}")
                screenrc.append("focus")
        screenrc.append(f"layout save {layout_name}")
    screenrc.append("detach")
    screenrc.append("")
    return screenrc


def _calc_size(children):
    """Add size parameter if any of the children has it specified."""
    sizes = [c.size for c in children if c.size]
    if sizes and len(sizes) < len(children):
        size_left = 100 - sum(sizes)
        for c in children:
            if not c.size:
                c.size = size_left // (len(children) - len(sizes))
    return children


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
