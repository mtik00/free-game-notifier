#!/usr/bin/env python3

import argparse
import os
import re
import sys
import logging

import feedparser
import requests

from .logger import get_logger

__version__ = "0.1.0"

URL = "https://steamcommunity.com/groups/freegamesfinders/rss/"
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK") or None
LOGGER = get_logger()


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "-d", "--debug", help="Print debugging information.", action="store_true"
    )
    parser.add_argument(
        "--no-slack",
        help="Don't actually send the Slack message, just log it.",
        action="store_true",
    )
    parser.add_argument(
        "--filename", help="The name of the local file to read instead of hitting Steam"
    )
    parser.add_argument(
        "--webhook",
        help="The Slack webhook to post the message to.  Also: ${SLACK_WEBHOOK}",
    )
    return parser.parse_args(args)


def main(slack=True, feed_url=URL, webook=SLACK_WEBHOOK):
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

    if slack:
        LOGGER.debug("Sending slack message...")
        response = requests.post(webook, json=data)
        response.raise_for_status()
        LOGGER.debug("...done")
    else:
        LOGGER.debug("Not sending slack message")
        LOGGER.debug(data)


def run():
    """Parse the arguments and call the main function."""
    args = parse_args()

    slack = not args.no_slack

    feed_url = URL
    if args.filename:
        feed_url = args.filename

    webook = args.webhook or SLACK_WEBHOOK
    
    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    main(slack=slack, feed_url=feed_url, webook=webook)


if __name__ == "__main__":
    run()
