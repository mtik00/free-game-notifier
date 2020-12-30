#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.parse import urlparse


def icon_from_url(url: str):
    """
    A very simple attempt at matching up a game URL with its representing icon.
    We attempt to parse the URL and return the favicon.  If that fails, return
    a pre-determined image based on the URL.
    """
    if not url:
        return

    parts = urlparse(url)
    if parts.netloc:
        return f"{parts.scheme}://{parts.netloc}/favicon.ico"

    if "steam" in url:
        return "https://store.steampowered.com/favicon.ico"
    elif "epic" in url:
        return "https://www.epicgames.com/favicon.ico"

    return None
