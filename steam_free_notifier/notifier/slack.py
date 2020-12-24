#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module that communicates with Slack.
"""


from ..abc.notifier import Notifier

class Webhook(Notifier):

    def send(self, item):
        ...
