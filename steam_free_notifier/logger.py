#!/usr/bin/env python3
import logging
import os

import pendulum

from .settings import get_settings


__logger = None


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""
    def __init__(self, timezone, *args, **kwargs):
        self._timezone = timezone
        super().__init__(*args, **kwargs)

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


def get_logger():
    """
    You can use this function to retreive the application logger while ensuring
    it is set up correctly.
    """
    global __logger

    if __logger is None:
        __logger = logging.getLogger("steam_free_notifier")
        handler = logging.StreamHandler()
        handler.setFormatter(
            Formatter(
                get_settings()["timezone"],
                fmt="%(asctime)s %(levelname)s: %(message)s",
                datefmt="%m/%d/%Y %H:%M:%S %Z",
            )
        )

        logging.basicConfig(level=logging.INFO, handlers=[handler])

    return __logger
