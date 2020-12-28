#!/usr/bin/env python3
import logging
import os

import pendulum

from .config import configuration

__logger = None


def shorten_path(path):
    """
    This seems like a pretty bad idea, but I'm doing it anyway.
    I want to convert an asbolute path to a kind of module-relative path.

    Something like:
        /usr/src/app/free_game_notifier/notifier/slack.py
    would be shortend to:
        notifier/slack.py
    """
    base, _ = os.path.split(__file__)
    return path.replace(base + os.path.sep, "")


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def __init__(self, timezone, *args, **kwargs):
        self._timezone = timezone
        super().__init__(*args, **kwargs)

    def format(self, record):
        """shorten the absolute path"""
        record.pathname = shorten_path(record.pathname)
        return super().format(record)

    def converter(self, timestamp):
        dt = pendulum.from_timestamp(timestamp)
        return dt.in_tz(self._timezone)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s


def set_root_level(level):
    logging.getLogger().setLevel(level)


handler = logging.StreamHandler()
handler.setFormatter(
    Formatter(
        configuration.get("timezone", "UTC"),
        fmt="%(asctime)s {%(pathname)20s:%(lineno)3s} %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S %Z",
    )
)

logging.basicConfig(level=logging.INFO, handlers=[handler])
