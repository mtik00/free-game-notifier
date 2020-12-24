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
from .steam.item import Item as SteamItem
from .steam.feed import Feed as SteamFeed
from .logger import get_logger
from .settings import settings

LOGGER = get_logger()


def process_item(item):
    pass


def process_feed(feed):
    pass


def main(
    # url: str = typer.Option(..., envvar="SFN_APP_URL"),
    # webhook: str = typer.Option(None, envvar="SFN_APP_WEBHOOK"),
    # verbose: bool = typer.Option(False, envvar="SFN_APP_VERBOSE"),
    # cache_path: str = typer.Option(None, envvar="SFN_APP_CACHE_PATH"),
    # settings_path: str = typer.Option(None, envvar="SFN_APP_SETTINGS_PATH"),
):
    cache = Cache(path=settings["cache_path"])
    if settings["verbose"] or settings["debug"]:
        LOGGER.setLevel(logging.DEBUG)

    feed = SteamFeed(settings["feeds"]["steam"]["url"])
    item = feed.get()
    cached_data = cache.get(item.title)
    if cached_data and cached_data["posted"]:
        LOGGER.debug(
            f"Item '{cached_data['title']}' already posted on {time.asctime(time.localtime(cached_data['posted']))}"
        )
        return

    slack_data = item.to_slack_message()

    webhook = settings["notifiers"]["slack"]["url"]
    if webhook:
        LOGGER.debug("Sending slack message...")

        if settings["verbose"]:
            LOGGER.debug(pformat(slack_data))

        response = requests.post(webhook, json=slack_data)
        response.raise_for_status()
        item.posted = time.time()
        cache.add(item.to_dict())
        cache.save()
        LOGGER.debug("...done")
    else:
        LOGGER.debug("No webhook defined...")
        LOGGER.debug(pformat(slack_data))
        cache.add(item.to_dict())
        cache.save()


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
