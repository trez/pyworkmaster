import sys
import os
import logging
from pprint import pprint

from pyworkmaster.config import Config
import pyworkmaster.screen as s
from pyclicommander import Commander

_log = logging.getLogger(__name__)

commander = Commander(cmd_name="workmaster")
config = None


@commander.cli("PROJECT config")
def wm_config_get(project):
    """ Get configuration for a project. """
    __for_project(lambda p: pprint(config[p]), project=project)


@commander.cli("PROJECT attach")
def wm_attach(project, setup=False):
    """ Attach to a project workspace.
    """
    _assert_project_defined(project)

    if not s.is_setup(project):
        s.setup(config[project])

    s.attach(project)


@commander.cli("PROJECT kill")
def wm_kill(project):
    """ Kill a project workspace. """
    def _kill(project):
        if not s.is_setup(project):
            print("Project not setup.")
            return -1
        s.kill(project)

    __for_project(_kill, project=project)


@commander.cli("PROJECT")
def wm_project(project):
    __for_project(lambda p: print(f"{project=}"), project=project)


@commander.cli("current")
def wm_current_name():
    """ Name current session. """
    __for_project(print)


@commander.cli("current kill")
def wm_current_kill():
    """ Kill current session. """
    __for_project(s.kill)


@commander.cli("current config")
def wm_current_config():
    """ Get config for current session. """
    __for_project(wm_config_get)


@commander.cli("")
def wm_main():
    """ List all available projects found in config. """
    for proj in sorted(config):
        print((f"{'* ' if s.is_setup(proj) else ''}{proj}"))


def __for_project(run_f, project=None):
    if project is None:
        project = _get_current_session()

    if project and project in config:
        return run_f(project)
    elif project not in config:
        print("Not configured workmaster project")
    else:
        print("Could not figure out current project")


def main():
    global config
    config = Config()
    _setup_logging(config)
    _log.debug(f"CONFIG:\n{config}")

    return commander.call_with_help()


def _assert_project_defined(project):
    if project not in config:
        print("Unknown project")
        sys.exit(1)


def _get_current_session():
    if screen_env := os.environ.get('STY'):
        pid, project = screen_env.split(".", 1)
        return project
    return None


def _setup_logging(config):
    handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=config.get_global("log_level"),
        format="%(levelname)s:%(asctime)s:%(name)s:%(message)s",
        handlers=handlers,
    )


if __name__ == "__main__":
    sys.exit(main())
