#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to keep the application settings.
"""
import os

from yaml import load, Loader


LOCAL_TZ = (
    os.environ.get("SFN_APP_LOCAL_TIMEZONE", "UTC").replace('"', "").replace("'", "")
)

SETTINGS_PATH = os.environ.get("SFN_APP_SETTINGS_PATH")


DEFAULTS = {
    "timezone": "UTC"
}

class Settings:
    def __init__(self, path=None):
        self._settings = {}
        self.load(path)
    
    def __getitem__(self, key):
        return self._settings.get(key)

    def load(self, path=None):
        if path and os.path.exists(path):
            with open(path) as fh:
                self._settings = load(fh, Loader=Loader)


settings = Settings(SETTINGS_PATH)
