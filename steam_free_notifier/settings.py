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


class _Settings:
    __settings = None

    def __init__(self):
        if _Settings.__settings is None:
            _Settings.__settings = self
            _Settings.__settings.configure(path=None)

    def configure(self, path):
        self._settings = DEFAULTS
        self.load(path)

    def __getitem__(self, key):
        return self._settings.get(key)

    def load(self, path=None):
        if path and os.path.exists(path):
            with open(path) as fh:
                self._settings.update(load(fh, Loader=Loader))


settings = _Settings()
