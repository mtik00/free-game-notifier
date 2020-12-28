#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A base class to provide a default interface for a Notifier.
"""
from abc import ABC, abstractmethod
import logging

from ..abc.item import Item

LOGGER = logging.getLogger(__name__)


class Notifier:
    location: str

    def __init__(self, url):
        self.url = url

    def send(self, item: Item):
        LOGGER.debug("Would be sending item: %r", item)
