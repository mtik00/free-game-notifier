#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module retreives and reads a feed from the Steam freegames community.
"""
import hashlib
import os
import re
import time

import feedparser
import pendulum
import requests
from jinja2 import Template
from lxml import html

from ..abc.feed import Feed as BaseFeed
from ..abc.item import Item as BaseItem
from ..icons import icon_from_url
from ..logger import get_logger
from ..notifier.slack import Notifier as SlackNotifier
from ..settings import get_settings

LOGGER = get_logger()

SLACK_BODY_TEMPLATE = """*{{title}}*
{%- if good_through %}
Offer good through {{ good_through }}
{%- endif %}
{% if rating -%}
Recent reviews: {{rating}}
{%- endif %}

Links:
{% if game_link -%}
- <{{game_link}}|Offer Redemption>
{%- endif %}
{% if steam_store_link -%}
- <{{steam_store_link}}|Steam Store Page for reference>
{% endif -%}
- <{{ steam_link }}|Steam Announcement>

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
        new_date = " ".join(parts[:-1]) + f" {pendulum.now(tz=tz).year}"
        try:
            p = pendulum.from_format(new_date, fmt="MMMM D, Hmm YYYY", tz=tz)
            return p.in_tz(get_settings()["timezone"]).format("dddd D-MMM at hA zz")
        except Exception as e:
            LOGGER.error("Could not parse the date: %s", e)

    return ""


def parse_steam_store_link(summary: str) -> str:
    """Search the summary for a steampowered URL."""
    # Sample URL:
    # href="https://store.steampowered.com/app/314660/Oddworld_New_n_Tasty/"
    if match := re.search(r'href="(https://store.steampowered.*?)"', summary):
        return match.group(1)
    else:
        LOGGER.warn("Could not parse steam store page")
        LOGGER.debug(summary)

    return ""


def steam_app_rating(html_text):
    tree = html.fromstring(html_text)
    items = tree.xpath(
        '//div[contains(@class, "user_reviews_summary_bar")]'
        '/div[contains(string(), "Recent Reviews")]'
        '/span[contains(@class, "game_review_summary")]/text()'
    )

    if items:
        return items[0]
    else:
        LOGGER.debug("Could not parse rating")

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
        self.steam_store_link = parse_steam_store_link(self.summary)

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

    def get_steam_store_html(self):
        html = None
        if self.steam_store_link and os.path.isfile(self.steam_store_link):
            with open(self.steam_store_link) as fh:
                html = fh.read()
        elif self.steam_store_link:
            response = requests.get(self.steam_store_link)
            response.raise_for_status()
            html = response.text

        return html

    def to_slack_message(self):
        rating = None
        if (html := self.get_steam_store_html()) :
            rating = steam_app_rating(html)

        t = Template(SLACK_BODY_TEMPLATE)
        body = t.render(
            title=self.title,
            rating=rating,
            game_link=self.game_link,
            good_through=self.good_through,
            steam_link=self.steam_link,
            steam_store_link=self.steam_store_link,
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
                        "image_url": icon_from_url(self.game_link),
                        "alt_text": "steam logo",
                    },
                },
            ],
        }


class Feed(BaseFeed):
    url: str = "https://steamcommunity.com/groups/freegamesfinders/rss/"

    def __init__(self, cache, url=None, webook=None):
        self.cache = cache
        self.url = url or Feed.url
        self.webhook = webook
        self.read(url)

    def read(self, url=None):
        feed_url = url or self.url
        self._feed = feedparser.parse(feed_url)
        if not self._feed.items:
            LOGGER.warn("No items found in %s", feed_url)
        else:
            LOGGER.debug("Found %d items in %s", len(self._feed.entries), feed_url)

    def get(self, index=0) -> Item:
        element = None
        if len(self._feed.get("items", 0)) > index + 1:
            element = self._feed["items"][index]

        if element:
            return Item.from_rss_element(element)

        return element
