#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A base class to provide a default interface for a Notifier.
"""

from abc import ABC, abstractmethod

from ..abc.item import Item
import logging

LOGGER = logging.getLogger("steam_free_notifier")


class Notifier:
    location: str

    def __init__(self, url, cache):
        self.url = url
        self.cache = cache

    def send(self, item: Item):
        LOGGER.debug("Would be sending item: %r", item)

    def completed(self, item: Item):
        """
        Stores the item in the cache as completed.
        """
        self.cache.add(item.to_dict())
        self.cache.save()
