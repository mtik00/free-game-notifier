#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module retreives and reads a feed from the Steam freegames community.
"""
import datetime
import logging
import os
import re

import feedparser
import pendulum
import requests
from jinja2 import Template
from lxml import html

from ..abc.feed import Feed as BaseFeed
from ..abc.item import Item as BaseItem
from ..config import configuration
from ..icons import icon_from_url
from ..notifier.slack import Notifier as SlackNotifier

LOGGER = logging.getLogger(__name__)

SLACK_BODY_TEMPLATE = """*{{title}}*
{%- if good_through %}
Offer good through {{ good_through }}
{%- endif %}
{%- if ratings %}
{% if ratings.recent and ratings.overall %}Recent reviews: {{ratings.recent}}
Overall reviews: {{ratings.overall}}
{%- elif ratings.recent %}
Recent reviews: {{ratings.recent}}
{%- else %}
Overall reviews: {{ratings.overall}}
{%- endif -%}
{% endif %}

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
    if match := re.search(r"Offer good (through|thru) (?P<date>.*?)\<br", summary):
        parts = match.group("date").split()
        tz = parts[-1]
        try:
            new_date = " ".join(parts[:-1]) + f" {pendulum.now(tz=tz).year}"
            p = pendulum.from_format(new_date, fmt="MMMM D, Hmm YYYY", tz=tz)
            dt = p.in_tz(configuration["timezone"])
            return dt.format("dddd D-MMM at hA zz"), dt
        except Exception as e:
            LOGGER.error("Could not parse the date: %s", e)

    return "", None


def parse_pubdate(pubdate: str) -> pendulum.DateTime:
    """
    Converts the pubDate element to a pendulum DateTime.

    pubDate looks like this:

        Wed, 30 Dec 2020 16:00:01 +0000
    """
    fmt = "ddd, DD MMM YYYY HH:mm:ss ZZ"
    try:
        return pendulum.from_format(pubdate, fmt)
    except Exception:
        LOGGER.warning("Could not parse pubdate: %s", pubdate)

    return None


def to_pendulum(date: datetime.date) -> pendulum.DateTime:
    if not date:
        return None

    dt = datetime.datetime.combine(date, datetime.datetime.min.time())
    return pendulum.instance(dt)


def parse_steam_store_link(summary: str) -> str:
    """Search the summary for a steampowered URL."""
    # Sample URL:
    # href="https://store.steampowered.com/app/314660/Oddworld_New_n_Tasty/"
    if match := re.search(r'href="(https://store.steampowered.*?)"', summary):
        return match.group(1)
    else:
        LOGGER.warning("Could not parse steam store page.  Here's the summary:")
        LOGGER.debug(summary)

    return ""


def steam_recent_app_rating(html_text):
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


def steam_all_app_rating(html_text):
    tree = html.fromstring(html_text)
    items = tree.xpath(
        '//div[contains(@class, "user_reviews")]'
        '/div[contains(string(), "Overall Reviews")]'
        '/span[contains(@class, "game_review_summary")]/text()'
    )

    if items:
        return items[0]
    else:
        LOGGER.debug("Could not parse rating")

    return ""


def steam_ratings(html_text):
    """Tries to get both 'all' and 'recent' ratings."""
    return {
        "overall": steam_all_app_rating(html_text),
        "recent": steam_recent_app_rating(html_text),
    }


class Item(BaseItem):
    def __init__(
        self,
        title: str,
        summary: str,
        steam_link: str,
        game_link: str = None,
        posted=None,
        good_through: str = None,
        published: str = None,
    ):
        self.title = title
        self.summary = summary
        self.steam_link = steam_link
        self.game_link = game_link
        self.posted = posted
        self.good_through, self.good_through_datetime = parse_good_through(self.summary)
        self.steam_store_link = parse_steam_store_link(self.summary)

        self.published = published
        self.published_datetime = parse_pubdate(self.published)

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
            published=element["published"],
        )

    @staticmethod
    def from_dict(data):
        return Item(
            title=data["title"],
            summary=data["summary"],
            steam_link=data["steam_link"],
            game_link=data["game_link"],
            posted=data.get("posted"),
            published=data.get("published"),
        )

    def to_dict(self):
        return {
            "title": self.title,
            "summary": self.summary,
            "steam_link": self.steam_link,
            "game_link": self.game_link,
            "posted": self.posted or "",
            "published": self.published,
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
        ratings = None
        if (html := self.get_steam_store_html()) :
            ratings = steam_ratings(html)

        t = Template(SLACK_BODY_TEMPLATE)
        body = t.render(
            title=self.title,
            ratings=ratings,
            game_link=self.game_link,
            good_through=self.good_through,
            steam_link=self.steam_link,
            steam_store_link=self.steam_store_link,
        )

        data = {
            "text": self.title,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": body,
                    },
                },
            ],
        }

        icon_url = icon_from_url(self.game_link or self.steam_link)
        if icon_url:
            data["blocks"][0]["accessory"] = {
                "type": "image",
                "image_url": icon_url,
                "alt_text": "store logo",
            }

        return data


class Feed(BaseFeed):
    url: str = "https://steamcommunity.com/groups/freegamesfinders/rss/"

    def __init__(self, url=None, webook=None):
        self.url = url or Feed.url
        self.webhook = webook
        self.read(url)

    def read(self, url=None):
        feed_url = url or self.url
        self._feed = feedparser.parse(feed_url)
        if not self._feed.items:
            LOGGER.warning("No items found in %s", feed_url)
        else:
            self.filter_pubdate()
            LOGGER.debug("Found %d items in %s", len(self._feed.entries), feed_url)

    def filter_pubdate(self):
        """Filters out any of our items that were published prior to the setting."""
        start_date = to_pendulum(configuration.get("start_date"))

        if not start_date:
            return

        result = []

        LOGGER.debug(
            "filtering all items older than %s", start_date.format("YYYY-MMM-DD")
        )
        for item in self._feed["items"]:
            pubdate = parse_pubdate(item["published"])
            if not pubdate or (pubdate >= start_date):
                result.append(item)
            else:
                LOGGER.debug(
                    "Item too old: %s %s",
                    item["title"][:10],
                    pubdate.format("YYYY-MMM-DD"),
                )

        self._feed["items"] = result

    def get(self, index=0) -> Item:
        element = None
        if len(self._feed.get("items", 0)) > index + 1:
            element = self._feed["items"][index]

        if element:
            return Item.from_rss_element(element)

        return element

    def get_items(self, count=1, filtered=True) -> list[Item]:
        for element in self._feed["items"][:count]:
            item = Item.from_rss_element(element)

            if not filtered:
                yield item
            elif not is_item_ignored(item):
                yield item


def is_item_expired(item: Item) -> bool:
    expired = False
    if (
        item.good_through_datetime
        and pendulum.now(tz=configuration["timezone"]) >= item.good_through_datetime
    ):
        LOGGER.debug("offer expired for %s...", item.title[:20])
        expired = True

    return expired


def is_item_ignored_by_url(item: Item) -> bool:
    ignore_rules = configuration.get("ignore", {})

    for url_search in ignore_rules.get("urls", []):
        for url in [item.steam_link, item.steam_store_link, item.game_link]:
            if not url:
                continue

            if re.search(url_search, url, re.IGNORECASE):
                LOGGER.debug("Ignoring url: %s", url)
                return True

    return False


def is_item_ignored_by_title(item: Item) -> bool:
    ignore_rules = configuration.get("ignore", {})

    for title_search in ignore_rules.get("titles", []):
        if item.title and re.search(title_search, item.title, re.IGNORECASE):
            return True

    return False


def is_item_ignored(item: Item) -> bool:
    return (
        is_item_ignored_by_title(item)
        or is_item_ignored_by_url(item)
        or is_item_expired(item)
    )
