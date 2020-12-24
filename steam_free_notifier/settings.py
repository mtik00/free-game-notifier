#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to keep the application settings.
"""
import os

from yaml import Loader, load

SETTINGS_PATH = os.environ.get("SFN_APP_SETTINGS_PATH")


DEFAULTS = {
    "timezone": "UTC",
    "feeds": {"steam": {"url": os.environ.get("SFN_APP_URL")}},
    "notifiers": {"slack": {"url": os.environ.get("SFN_APP_WEBHOOK")}},
    "verbose": os.environ.get("SFN_APP_VERBOSE"),
}


class Settings:
    def __init__(self, path=None):
        self._settings = DEFAULTS
        self.load(path)

    def __getitem__(self, key):
        return self._settings.get(key)

    def load(self, path=None):
        if path and os.path.exists(path):
            with open(path) as fh:
                self._settings.update(load(fh, Loader=Loader))


settings = Settings(SETTINGS_PATH)
