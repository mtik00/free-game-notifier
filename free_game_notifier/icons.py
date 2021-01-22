#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import logging

import requests

from .config import configuration

LOGGER = logging.getLogger(__name__)
STEAM_ICON = "https://store.steampowered.com/favicon.ico"
EPIC_ICON = "https://www.epicgames.com/favicon.ico"


def icon_from_url(url: str):
    """
    A very simple attempt at matching up a game URL with its representing icon.
    We attempt to parse the URL and return the favicon.  If that fails, return
    a pre-determined image based on the URL.
    """
    if not url:
        return

    # Allow the user to override icons in the configuration
    for partial_string, icon_url in configuration.get("icons").items():
        if partial_string in url:
            return icon_url

    # Try some known-good icons
    if "steam" in url:
        return STEAM_ICON
    elif "epic" in url:
        return EPIC_ICON

    # Try the site's favicon
    parts = urlparse(url)
    if parts.netloc:
        icon_url = f"{parts.scheme}://{parts.netloc}/favicon.ico"
        response = requests.get(icon_url)
        try:
            response.raise_for_status()
            return icon_url
        except requests.HTTPError:
            LOGGER.warning(
                "Invalid icon URL (return code %s): %s", response.status_code, icon_url
            )
        except requests.ConnectionError as e:
            LOGGER.warning("Error while connecting to %s: %s", icon_url, e)

    return None
