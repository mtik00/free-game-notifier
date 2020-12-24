#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module retreives and reads a feed from the Steam freegames community and
optionally posts the result.
"""
import time

import feedparser

from ..logger import get_logger
from .item import Item

LOGGER = get_logger()


class Feed:
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
