import sys
import os
import logging

from pyworkmaster.config import Config
import pyworkmaster.screen as s
from pyclicommander import Commander

_log = logging.getLogger(__name__)

commander = Commander(cmd_name="workmaster")
config = None


@commander.cli("list")
def wm_list():
    """ List all available projects found in config. """
    for proj in config:
        print((f"{'* ' if s.is_setup(proj) else ''}{proj}"))


@commander.cli("config")
def wm_config():
    """ Configuration management. """
    commander.help(["config"])


@commander.cli("config get PROJECT")
def wm_config_get(project):
    """ Get configuration for a project. """
    if project not in config:
        print("Unknown project")
        return -1

    print(config[project])


@commander.cli("setup PROJECT")
def wm_setup(project):
    """ Setup an initial project workspace. """
    if project not in config:
        print("Unknown project")
        return -1

    s.setup(config[project])


@commander.cli("attach [--setup] [PROJECT]")
def wm_attach(project=None, setup=False):
    """ Attach to a project workspace.

    Flags
    -----
    --setup   Setup project if not setup before attaching.
    """

    if project is None:
        setup_projects = [proj for proj in config if s.is_setup(proj)]
        for proj in setup_projects:
            print((f"* {proj}"))
    else:
        if project not in config:
            print("Unknown project")
            return -1

        if not s.is_setup(project):
            if setup:
                s.setup(config[project])
            else:
                print("Project not setup.")
                return -1

        s.attach(project)


@commander.cli("kill PROJECT")
def wm_kill(project):
    """ Kill a project workspace. """
    if project not in config:
        print("Unknown project")
        return -1

    if not s.is_setup(project):
        print("Project not setup.")
        return -1

    s.kill(project)


@commander.cli("task")
def wm_task_run():
    """ Run a task for attached project. """
    commander.help(["task"])


@commander.cli("")
def wm_main():
    """ Workmaster cli. """
    commander.help()


def handle_tasks(project, task):
    for window, cmd in config[project]["tasks"][task]["cmds"]:
        s.run_command(project, window, cmd)


def main():
    global config
    config = Config()
    _setup_logging(config)
    _log.debug(f"CONFIG:\n{config}")

    # Register each project specific task as a new cli.
    if (current_project := _get_current_session()) and current_project in config:
        for task, taskinfo in config[current_project]["tasks"].items():
            kwargs = {k: taskinfo[k] for k in taskinfo if k in ["short_description", "long_description"]}
            commander.add_cli(f"task {task}", lambda: handle_tasks(current_project, task), **kwargs)

    return commander.call_with_help()


def _get_current_session():
    if screen_env := os.environ.get('STY'):
        pid, project = screen_env.split(".", 1)
        return project
    return None


def _setup_logging(config):
    # handlers = [logging.FileHandler('output.log')]
    handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=config.get_global("log_level"),
        format="%(levelname)s:%(asctime)s:%(name)s:%(message)s",
        handlers=handlers,
    )


if __name__ == "__main__":
    sys.exit(main())
