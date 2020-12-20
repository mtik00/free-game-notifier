#!/usr/bin/env python3

import logging
import os
import re
import sys
from pprint import pformat
import time

import feedparser
import requests
from envargparse import EnvArgParser

from .cache import Cache
from .item import Item
from .logger import get_logger

LOGGER = get_logger()


def bool_envvar_to_envargparser(*args):
    """
    EnvArgParser doesn't do a good job at handling flags.  This function will
    convert "sane" inputs to something that EnvArgParser will understand as a
    boolean.

    EnvArgParser will treat an empty string as `True`, and everthing else as an
    error.

    The end result of this function is either removing the environment variable
    or setting it to an empty string.
    """
    for name in args:
        if (value := os.environ.get(name)) is not None:
            if (not value) or (value.lower()[0] in ["n", "0", "f"]):
                # remove the env var if it's anything that's "False"
                os.environ.pop(name)
            else:
                # Assume that the user wishes to enable debug.
                # The env var must be an empty string for EnvArgParser to successfully
                # convert it.
                os.environ[name] = ""


def parse_args(args=sys.argv[1:]):
    bool_envvar_to_envargparser("SFN_APP_DEBUG", "SFN_APP_VERBOSE")

    parser = EnvArgParser(description="Scrap an RSS feed and post to a webhook.")
    parser.add_argument(
        "-d",
        "--debug",
        help="Print debugging information.  Also set by $SFN_APP_DEBUG",
        env_var="SFN_APP_DEBUG",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print more debugging information.  Also set by $SFN_APP_VERBOSE",
        env_var="SFN_APP_VERBOSE",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--url",
        help="The file or URL from which to read the RSS feed.  Also set by $SFN_APP_URL",
        env_var="SFN_APP_URL",
        required=True,
    )
    parser.add_argument(
        "--webhook",
        help="The Slack webhook to post the message to.  Also set by $SFN_APP_WEBHOOK",
        env_var="SFN_APP_WEBHOOK",
    )
    parser.add_argument(
        "--cache-path",
        help="The path to the cache file.  Also set by $SFN_APP_CACHE_PATH",
        env_var="SFN_APP_CACHE_PATH",
    )
    return parser.parse_args(args)


def main(feed_url, webhook=None, verbose=False, cache_path=None):
    cache = Cache(path=cache_path)

    LOGGER.debug(f"reading feed from {feed_url}")
    feed = feedparser.parse(feed_url)
    first_item = feed["items"][0]

    cached_item = cache.get(first_item["title"])
    if cached_item and cached_item["posted"]:
        LOGGER.debug(
            f"Item '{cached_item['title']}' already posted on {time.asctime(time.localtime(cached_item['posted']))}"
        )
        return

    item = Item(
        title=first_item["title"],
        summary=first_item["summary"],
        slack_link=first_item["link"],
    )
    data = item.to_slack_message()

    if webhook:
        LOGGER.debug("Sending slack message...")

        if verbose:
            LOGGER.debug(pformat(data))

        response = requests.post(webhook, json=data)
        response.raise_for_status()
        item.posted = time.time()
        cache.add(item.to_dict())
        cache.save()
        LOGGER.debug("...done")
    else:
        LOGGER.debug("No webhook defined...")
        LOGGER.debug(pformat(data))


def run():
    """Parse the arguments and call the main function."""
    args = parse_args()

    if args.debug or args.verbose:
        LOGGER.setLevel(logging.DEBUG)

    main(
        feed_url=args.url,
        webhook=args.webhook,
        verbose=args.verbose,
        cache_path=args.cache_path,
    )


if __name__ == "__main__":
    run()
