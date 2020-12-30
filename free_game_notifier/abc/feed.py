#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A base class to provide a default interface for a Feed.
"""

from abc import ABC, abstractmethod


class Feed(ABC):
    url: str

    @abstractmethod
    def read(self, url):
        ...

    @abstractmethod
    def get(self, index=0):
        ...

    @abstractmethod
    def get_items(self, count=1):
        ...

    @abstractmethod
    def get_nonexpired_items(self, count=1):
        ...
