#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A base class to provide a default interface for an Item.
"""

from abc import ABC, abstractmethod, abstractstaticmethod

from pendulum import DateTime


class Item(ABC):
    good_through_datetime: DateTime
    good_through: str
    offer_link: str
    origin_link: str
    posted: str
    published_datetime: DateTime
    summary: str
    title: str

    @abstractmethod
    def __eq__(self, other):
        ...

    @staticmethod
    @abstractstaticmethod
    def from_rss_element(element):
        ...

    @staticmethod
    @abstractstaticmethod
    def from_dict(data):
        ...

    @abstractmethod
    def to_dict(self):
        ...

    @abstractmethod
    def format_message(self):
        ...
