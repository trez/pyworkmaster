import sys
import logging

from pyworkmaster.config import Config
import pyworkmaster.screen as s
from pyclicommander import Commander

_log = logging.getLogger(__name__)

commander = Commander(cmd_name="workmaster")
config = None


@commander.cli("list")
def wm_list():
    for proj in config:
        print(proj)


@commander.cli("config get PROJECT")
def wm_config_get(project):
    print(config[project])


@commander.cli("setup PROJECT")
def wm_setup(project):
    if project not in config:
        print("Unknown project")
        return -1

    s.run(config, project)


def main():
    global config
    config = Config()
    _setup_logging(config)
    _log.debug(f"CONFIG:\n{config}")
    return commander.call_with_help()


def _setup_logging(config):
    # handlers = [logging.FileHandler('output.log')]
    handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=config.get_global('log_level'),
        format="%(levelname)s:%(asctime)s:%(name)s:%(message)s",
        handlers=handlers,
    )


if __name__ == "__main__":
    sys.exit(main())
