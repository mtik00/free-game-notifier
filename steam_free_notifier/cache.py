#!/usr/bin/env python3
"""
This module contains the cache for the application.

The cache is a simple JSON file stored in the `data_dir` folder.
"""
import json
import os

from .logger import get_logger

LOGGER = get_logger()


class Cache:
    def __init__(self, path=None):
        self.path = path
        self.data = self.load(self.path)

    def __setitem__(self, name, value):
        self.data[name] = value

    def __getitem__(self, name):
        return self.data.get(name)

    def get(self, title):
        return self.data.get(title)

    def add(self, d: dict):
        self.data[d["title"]] = d

    def load(self, path):
        if path and os.path.exists(path):
            with open(path) as fh:
                data = fh.read().strip() or "{}"

            data = json.loads(data)
        else:
            data = {}

        return data

    def save(self):
        if self.path:
            data = self.data or {}
            json_data = json.dumps(data)
            with open(self.path, "w") as fh:
                fh.write(json_data)
        else:
            LOGGER.warn("Cache.save() called without specifying a JSON file.")
