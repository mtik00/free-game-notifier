#!/usr/bin/env python3

import logging
import os
import re
import sys
import time
from pprint import pformat

import feedparser
import requests
import typer

from .cache import Cache
from .item import Item
from .logger import get_logger

LOGGER = get_logger()


def main(
    url: str = typer.Option(..., envvar="SFN_APP_URL"),
    webhook: str = typer.Option(None, envvar="SFN_APP_WEBHOOK"),
    verbose: bool = typer.Option(False, envvar="SFN_APP_VERBOSE"),
    cache_path: str = typer.Option(None, envvar="SFN_APP_CACHE_PATH"),
):
    cache = Cache(path=cache_path)
    if verbose:
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug(f"reading feed from {url}")
    feed = feedparser.parse(url)

    if len(feed["items"]) < 1:
        raise Exception("No items found in feed")

    # We're only interested in the first item from the RSS feed.
    item = Item.from_rss_element(feed["items"][0])

    cached_data = cache.get(item.title)
    if cached_data and cached_data["posted"]:
        LOGGER.debug(
            f"Item '{cached_data['title']}' already posted on {time.asctime(time.localtime(cached_data['posted']))}"
        )
        return

    slack_data = item.to_slack_message()

    if webhook:
        LOGGER.debug("Sending slack message...")

        if verbose:
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
