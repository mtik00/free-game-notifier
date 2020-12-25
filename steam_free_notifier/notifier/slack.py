#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module that communicates with Slack.
"""
import time
from pprint import pformat

import requests

from ..abc.notifier import Notifier as BaseNotifier
from ..logger import get_logger

LOGGER = get_logger()


class Notifier(BaseNotifier):
    notifier_type: str = "slack"

    def send(self, item):
        if not item:
            LOGGER.error("item is not defined")
            return

        slack_data = item.format_message(self)
        LOGGER.debug(pformat(slack_data))

        if self.url:
            response = requests.post(self.url, json=slack_data)
            response.raise_for_status()
            item.posted = time.time()
            super().completed(item)
            LOGGER.debug("...done")
        else:
            LOGGER.debug("`url` not defined; not notifying Slack")
