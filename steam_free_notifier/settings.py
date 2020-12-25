#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to keep the application settings.
"""
import os

from yaml import Loader, load

from .boolean_utils import to_bool

DEFAULTS = {
    "timezone": "UTC",
    "feeds": {"steam": {"url": os.environ.get("SFN_APP_URL")}},
    "notifiers": {"slack": {"url": os.environ.get("SFN_APP_WEBHOOK")}},
    "debug": to_bool(os.environ.get("SFN_APP_DEBUG")),
}

__settings = None


class _Settings:
    def __init__(self, path):
        self._settings = DEFAULTS
        self.load(path)

    def __getitem__(self, key):
        return self._settings.get(key)

    def load(self, path=None):
        if path and os.path.exists(path):
            with open(path) as fh:
                self._settings.update(load(fh, Loader=Loader))


def get_settings(path=os.environ.get("SFN_APP_SETTINGS_PATH")):
    """
    This should be called to retreive the current settings object instead of
    interacting directly with `__settings`.
    """
    global __settings

    if __settings is None:
        __settings = _Settings(path)
    elif path:
        __settings.load(path)

    return __settings
