#!/usr/bin/env python3
"""
This module contains the cache for the application.

The cache is a simple JSON file stored in the `data_dir` folder.
"""
import json
import os
from typing import Optional

import pendulum

from .logger import get_logger

LOGGER = get_logger()


class Cache:
    def __init__(self, path: Optional[str] = None, age: int = 90):
        self.path = path
        self.data = self.load(self.path)
        self.age = age

        if self.invalidate():
            self.save()

    def __setitem__(self, name, value):
        self.data[name] = value

    def __getitem__(self, name):
        return self.data.get(name)

    def __contains__(self, key):
        return key in self.data

    def get(self, title):
        return self.data.get(title)

    def add(self, key: str, d: dict):
        self.data[key] = d

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

    def invalidate(self, days_older_than: int = None):
        """
        Invalidate any cache items older than the specified number of days.
        """
        days_older_than = days_older_than or self.age

        if days_older_than:
            return

        keys_to_remove = set([])
        cleanup_date = pendulum.now(tz="UTC").subtract(days=days_older_than)

        for key, item in self.data.items():
            posted_date = pendulum.from_timestamp(item["posted"])
            if item["posted"] and (posted_date < cleanup_date):
                LOGGER.debug("invalidating %s (%s)", key, item["title"])
                keys_to_remove.add(key)

        if keys_to_remove:
            LOGGER.debug(
                "Invalidating %d cached entries older than %d days",
                len(keys_to_remove),
                self.age,
            )

            for key in keys_to_remove:
                self.data.pop(key)

            self.save()

        return len(keys_to_remove)
