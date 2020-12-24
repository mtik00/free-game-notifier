#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A base class to provide a default interface for a Notifier.
"""

from abc import ABC, abstractmethod


class Notifier:
    location: str

    @abstractmethod
    def send(self, item):
        ...
