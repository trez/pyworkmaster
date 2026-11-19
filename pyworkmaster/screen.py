import logging
import tempfile
import subprocess
import os

_log = logging.getLogger(__name__)
default_config = os.path.expanduser("~/.screenrc")



def escape_double_quotes(s: str) -> str:
    # Important: escape backslashes first so you don't double-escape
    s = s.replace('\\', r'\\')
    s = s.replace('"', r'\"')
    return s


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
            screenrc.append(f'stuff "{escape_double_quotes(cmd)}^M"')

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


def get_current_layout(p):
    subprocess.run(f"screen -S {p} -X layout show", shell=True)
 
    lastmsg_output = subprocess.run(
        f"screen -S {p} -Q lastmsg",
        shell=True,
        capture_output=True,
        text=True,
    )

    n, *name = lastmsg_output.stdout.split(" ")
    name = ' '.join(name)
    return name


def get_windows(p):
    windows_output = subprocess.run(
        f"screen -S {p} -Q windows '%n,%t,%f|'",
        shell=True,
        capture_output=True,
        text=True,
    )
    windows = [parse_title(w) for w in windows_output.stdout.split("|") if w]
    current_focus = [t for n,t,f in windows if f][0]
    process = subprocess.run(
        f"screen -S {p} -Q select .",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return windows, current_focus


def move(p, target, layout_name, layout):
    # move
    windows, current_focus = get_windows(p)
    layout.focus(current_focus)
    print(f"{p=} {layout_name=} {current_focus=} {layout=}")
    layout.focus(target)
    print(f"{p=} {layout_name=} {target=} {layout=}")
    moves = []
    rec_move(layout, current_focus, target, moves)


def rec_move(layout, current, target, moves, direction_forward=None, curr_split=None):
    if layout.is_split():
        print(f"SPLIT: {layout.name}")
        curr_split = layout.name
        for c in layout.children:
            print(f"{curr_split=} {direction_forward=}")
            if direction_forward is not None:
                if curr_split == "|" and direction_forward:
                    moves += ["LEFT"]
                elif curr_split == "|" and not direction_forward:
                    moves += ["RIGHT"]
                elif curr_split == "/" and direction_forward:
                    moves += ["UP"]
                elif curr_split == "/" and not direction_forward:
                    moves += ["DOWN"]
                    
            print(f"{moves=}")
            direction_forward, m = rec_move(c, current, target, moves, direction_forward, curr_split)
    else:
        print(f"WINDOW: {layout.name}")
        if layout.name == current:
            print("FOUND CURRENT")
            return False, moves
        if layout.name == target:
            print("FOUND TARGET")
            return True, moves
        return direction_forward, moves


        

        

    #process = subprocess.run(
    #    f"screen -S {p} -X focus up",
    #    shell=True,
    #    stdout=subprocess.DEVNULL,
    #    stderr=subprocess.STDOUT,
    #)

    return None #process.returncode == 0


def parse_title(w):
    n, title, status = w.split(",")
    return n, title, status == "*"


def has_focus(w):
    return '*' in w


def run_command(session, window, cmd):
    subprocess.run(f"screen -S {session} -p {window} -X stuff '{cmd}^M'", shell=True)
