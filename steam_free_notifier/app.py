#!/usr/bin/env python3

import os
import re
import sys
import logging

import feedparser
import requests
from envargparse import EnvArgParser

from .logger import get_logger

__version__ = "0.1.0"

URL = "https://steamcommunity.com/groups/freegamesfinders/rss/"
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK") or None
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
    bool_envvar_to_envargparser("SFN_APP_DEBUG")

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

    return parser.parse_args(args)


def main(feed_url, webook=None):
    LOGGER.debug(f"reading feed from {feed_url}")
    feed = feedparser.parse(feed_url)
    first_item = feed["items"][0]

    title = first_item["title"]
    link = first_item["link"]

    # See if we can parse the direct link.
    if (
        match := re.search(
            'href="https://steamcommunity.*?url=(.*?)"', first_item["summary"]
        )
    ) :
        link = match.group(1)

    data = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{title}*\n{link}\n\nSteam link: {first_item['link']}",
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://store.steampowered.com/favicon.ico",
                    "alt_text": "steam logo",
                },
            },
        ]
    }

    if webook:
        LOGGER.debug("Sending slack message...")
        response = requests.post(webook, json=data)
        response.raise_for_status()
        LOGGER.debug("...done")
    else:
        LOGGER.debug("Not posting to webhook")
        LOGGER.debug(data)


def run():
    """Parse the arguments and call the main function."""
    args = parse_args()
    args.url

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    main(feed_url=args.url, webook=args.webhook)


if __name__ == "__main__":
    run()
