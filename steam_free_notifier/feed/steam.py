#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module retreives and reads a feed from the Steam freegames community.
"""
import hashlib
import re
import time

import feedparser
import pendulum
from jinja2 import Template

from ..abc.feed import Feed as BaseFeed
from ..abc.item import Item as BaseItem
from ..logger import get_logger
from ..notifier.slack import Notifier as SlackNotifier
from ..settings import get_settings

LOGGER = get_logger()

SLACK_BODY_TEMPLATE = """*{{title}}*
{%- if game_link %}
{{ game_link }}
{%- endif %}
{%- if good_through %}
Offer good through {{ good_through }}
{%- endif %}


Steam annoucement:
{{ steam_link }}
"""

def parse_good_through(summary: str) -> str:
    """
    Converts the "Good through" string in the announcement to the local timezone.

    If we can parse the date, this function will return a string that looks like:

        "Monday 21-Dec at 9AM MST"
    """
    # Pendulum doesn't handle the format.  We need to remove the timezone from
    # the string and add it as a parameter and add the year.
    # IOW, convert "December 21, 1600 GMT" to "December 21, 1600 2020".
    if match := re.search(r"Offer good through (.*?)\<br", summary):
        parts = match.group(1).split()
        tz = parts[-1]
        new_date = " ".join(parts[:-1]) + f" {pendulum.now().year}"
        try:
            p = pendulum.from_format(new_date, fmt="MMMM D, Hmm YYYY", tz=tz)
            return p.in_tz(get_settings()["timezone"]).format("dddd D-MMM at hA zz")
        except Exception as e:
            LOGGER.error("Could not parse the date: %s", e)

    return ""


class Item(BaseItem):
    def __init__(
        self,
        title: str,
        summary: str,
        steam_link: str,
        game_link: str = None,
        posted=None,
    ):
        self.title = title
        self.summary = summary
        self.steam_link = steam_link
        self.game_link = game_link
        self.posted = posted
        self.good_through = parse_good_through(self.summary)

        # See if we can parse the direct link.
        if (not game_link) and (
            match := re.search(
                'href="https://steamcommunity.*?url=(.*?)"', self.summary
            )
        ):
            self.game_link = match.group(1)

    def __eq__(self, other):
        return self.title == other.title

    @staticmethod
    def from_rss_element(element):
        return Item(
            title=element["title"],
            summary=element["summary"],
            steam_link=element["link"],
        )

    @staticmethod
    def from_dict(data):
        return Item(
            title=data["title"],
            summary=data["summary"],
            steam_link=data["steam_link"],
            game_link=data["game_link"],
            posted=data.get("posted"),
        )

    def to_dict(self):
        return {
            "title": self.title,
            "summary": self.summary,
            "steam_link": self.steam_link,
            "game_link": self.game_link,
            "posted": self.posted or "",
        }

    def format_message(self, notifier):
        if isinstance(notifier, SlackNotifier):
            return self.to_slack_message()

        raise NotImplementedError(f"Notifier type {type(notifier)} is not implemented")

    def to_slack_message(self):
        t = Template(SLACK_BODY_TEMPLATE)
        body = t.render(
            title=self.title,
            game_link=self.game_link,
            good_through=self.good_through,
            steam_link=self.steam_link
        )

        return {
            "text": self.title,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": body,
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "https://store.steampowered.com/favicon.ico",
                        "alt_text": "steam logo",
                    },
                },
            ],
        }

    def cache_key(self):
        """
        Returns the cachable key representing this item.
        """
        # Combine the title and the "good until" date.  That way subsequent
        # offers will be presented.
        h = hashlib.sha224()
        h.update(self.title.encode("utf-8"))
        h.update(self.good_through.encode("utf-8"))
        return h.hexdigest()


class Feed(BaseFeed):
    url: str = "https://steamcommunity.com/groups/freegamesfinders/rss/"

    def __init__(self, cache, url=None, webook=None):
        self.cache = cache
        self.url = url or Feed.url
        self.webhook = webook
        self.read(url)

    def read(self, url=None):
        self._feed = feedparser.parse(url or self.url)

    def get(self, index=0) -> Item:
        element = None
        if len(self._feed.get("items", 0)) > index + 1:
            element = self._feed["items"][index]

        if element:
            return Item.from_rss_element(element)

        return element
