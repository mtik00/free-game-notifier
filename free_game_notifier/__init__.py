#!/usr/bin/env python3
"""
This module is used to scrape the current free game from Epic Games and send a
notification.
"""
from importlib.metadata import version

try:
    __version__ = version(__name__)
except:
    pass
