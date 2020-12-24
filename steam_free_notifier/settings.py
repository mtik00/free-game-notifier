#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to keep the application settings.
"""
import os

LOCAL_TZ = (
    os.environ.get("SFN_APP_LOCAL_TIMEZONE", "UTC").replace('"', "").replace("'", "")
)


class Settings:
    def __init__(self, path):
        self._settings = {}
    

    def __getitem__(self, key):
        return self._settings.get(key)
