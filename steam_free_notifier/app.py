#!/usr/bin/env python3

import logging
import os
import re
import sys
import time
from pprint import pformat

import requests
import typer

from .cache import Cache
from .feed.steam import Item as SteamItem, Feed as SteamFeed
from .notifier.slack import Notifier as SlackNotifier
from .logger import get_logger
from .settings import get_settings

LOGGER = get_logger()


class_map = {"feeds": {"steam": SteamFeed}, "notifiers": {"slack": SlackNotifier}}


def get_class(category: str, name: str):
    item = class_map.get(category, {}).get(name)
    if not item:
        raise NotImplementedError(f"class type {category}.{name} is not implemented")

    return item


def main(
    settings_path: str = typer.Option(..., envvar="SFN_APP_SETTINGS_PATH"),
    debug: bool = typer.Option(False, envvar="SFN_APP_DEBUG"),
):
    settings = get_settings(settings_path)
    cache = Cache(path=settings["cache_path"])
    if debug or settings["debug"]:
        LOGGER.setLevel(logging.DEBUG)

    for feed_setting in settings["feeds"]:
        feed = get_class("feeds", feed_setting["type"])(
            url=feed_setting.get("url"), cache=cache
        )

        item = feed.get(index=0)

        for notifier_settings in settings["notifiers"]:
            notifier = get_class("notifiers", notifier_settings["type"])(
                url=notifier_settings.get("url"), cache=cache
            )
            notifier.send(item)


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
