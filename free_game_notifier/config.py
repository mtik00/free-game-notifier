#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module for dealing with application configuration in the form of a YAML
string or file.

The object acts like a mutable dictionary object.  Note, however, that there is
no `save()` method.  Any configuration items you set are considered temporary.

## dot-separated keys

You can request a nested configuration item using a dot-separate string using the
`by_path()` method.

For example:

    >>> config = Configuration(yaml)
    >>> yaml = '''
    ... base:
    ...     some_items: [0, 1, 2, 3]
    ...
    ...     another_config:
    ...         bin_folder: /usr/local/bin
    ...         sysbin_folder: /usr/sbin
    ... '''
    >>> config = Configuration(yaml)
    >>> config.by_path("base.another_config.sysbin_folder") == "/usr/sbin"
    True
    >>> config.by_path("base.some_items.3") == 3
    True

You can modify wether or not an exception is raised by an invalid key name using
either `raise_on_keyerror` when instantiating the object or when calling the
`by_path()` method.

This method tries to determine if the item being dereferenced is a list.  In that
case, and the key is an integer, the method will assume you are indexing into
the sequence and return the specified item.  See the example above.
"""
import logging
import os
from collections.abc import MutableMapping

import yaml

LOGGER = logging.getLogger(__name__)
DEFAULT_PATH = os.environ.get("SFN_APP_CONFIG_PATH")
DEFAULT = """
---
timezone: "UTC"
feeds:
    steam:
        -
notifiers:
    slack:
        -
debug: false
"""


class Configuration(MutableMapping):
    """YAML-based configuration object supporting a dict-like interface."""

    __instance = None

    def __init__(self, config=None, raise_on_keyerror: bool = True):
        if Configuration.__instance is None:
            self._config = {}
            self.raise_on_keyerror = bool(raise_on_keyerror)
            self.load_config(config or DEFAULT_PATH or DEFAULT)
            Configuration.__instance = self
        else:
            LOGGER.warn("Configuration.__init__ called again")

    def __getitem__(self, key):
        return self._config.__getitem__(key)

    def __len__(self):
        return len(self._config)

    def __iter__(self):
        return iter(self._config)

    def __setitem__(self, key, value):
        return self._config.__setitem__(key, value)

    def __delitem__(self, key):
        return self._config.__delitem__(key)

    def load_config(self, config):
        if os.path.isfile(config):
            with open(config) as fh:
                self._config = yaml.safe_load(fh)
        elif isinstance(config, str):
            self._config = yaml.safe_load(config)

    def by_path(self, path: str, raise_on_keyerror: bool = None):
        """
        Allows the use of nested keys.  E.g. "a.b.c"

        You can also index into a list by using an index number in your path.
        E.g. `base.some_list.1` asumes the following structure:

            base:
                some_list: ["first", "second", "third"]

        and would return "second".
        """
        raise_on_keyerror = (
            raise_on_keyerror
            if raise_on_keyerror is not None
            else self.raise_on_keyerror
        )
        get_func = "__getitem__" if raise_on_keyerror else "get"

        parts = path.split(".")

        item = getattr(self._config, get_func)(parts[0])

        if not item:
            return None

        for p in parts[1:]:
            # Separate list indexing because `list` only has __getitem__(), not get().
            if p.isdigit() and isinstance(item, list):
                item = item[int(p)]
            else:
                item = getattr(item, get_func)(p)

            # This is only needed when raise_on_keyerror is True.  We need to
            # stop the loop since None doesn't have the get methods.
            if item is None:
                break

        return item


configuration = Configuration()


if __name__ == "__main__":
    from pprint import pprint

    data = """
---
base:
    some_items: ["zero", "one", "two", "three", "four"]
    another_config:
        bin_folder: /usr/local/bin
        sysbin_folder: /usr/sbin
    """

    configuration.load_config(data)  # , raise_on_keyerror=False)
    pprint(configuration._config)
    pprint(configuration.by_path("base.some_items.1"))
