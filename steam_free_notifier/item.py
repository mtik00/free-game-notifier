#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A model that stores a single item.
"""
import re

from .logger import get_logger

LOGGER = get_logger()


class Item:
    def __init__(
        self,
        title: str,
        summary: str,
        slack_link: str,
        game_link: str = None,
        posted=None,
    ):
        self.title = title
        self.summary = summary
        self.slack_link = slack_link
        self.game_link = game_link
        self.posted = posted

        # See if we can parse the direct link.
        if (not game_link) and (
            match := re.search(
                'href="https://steamcommunity.*?url=(.*?)"', self.summary
            )
        ):
            self.game_link = match.group(1)

    def __eq__(self, other):
        return self.title == other.title

    @staticmethod
    def from_rss_element(element):
        return Item(
            title=element["title"],
            summary=element["summary"],
            slack_link=element["link"],
        )

    @staticmethod
    def from_dict(data):
        return Item(
            title=data["title"],
            summary=data["summary"],
            slack_link=data["slack_link"],
            game_link=data["game_link"],
            posted=data.get("posted"),
        )

    def to_dict(self):
        return {
            "title": self.title,
            "summary": self.summary,
            "slack_link": self.slack_link,
            "game_link": self.game_link,
            "posted": self.posted or "",
        }

    def to_slack_message(self):
        text = (
            f"*{self.title}*\n{self.game_link}\n\nSteam announcement: {self.slack_link}"
        )
        if not self.game_link:
            text = f"*{self.title}*\n\nSteam announcement: {self.slack_link}"

        return {
            "text": self.title,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text,
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "https://store.steampowered.com/favicon.ico",
                        "alt_text": "steam logo",
                    },
                },
            ],
        }
