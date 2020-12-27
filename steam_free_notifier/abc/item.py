#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A base class to provide a default interface for an Item.
"""

from abc import ABC, abstractmethod, abstractstaticmethod


class Item(ABC):
    title: str
    summary: str
    origin_link: str
    offer_link: str
    posted: str
    good_through: str

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
