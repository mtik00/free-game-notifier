#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from free_game_notifier.feed.steam import Item


def test_solitairica(solitairica, monkeypatch):
    item = Item.from_rss_element(solitairica)
    item.steam_store_link = "tests/steam/files/solitairica.html"
    with open(item.steam_store_link) as fh:
        html = fh.read()

    def mock_get_steam_store_html():
        return html

    monkeypatch.setattr(item, "get_steam_store_html", mock_get_steam_store_html)
    fmt = item.to_slack_message()
    print(fmt["blocks"][0]["text"]["text"])


def test_last_light(last_light, monkeypatch):
    item = Item.from_rss_element(last_light)
    item.steam_store_link = "tests/steam/files/last_light.html"
    with open(item.steam_store_link) as fh:
        html = fh.read()

    def mock_get_steam_store_html():
        return html

    monkeypatch.setattr(item, "get_steam_store_html", mock_get_steam_store_html)
    fmt = item.to_slack_message()
    print(fmt["blocks"][0]["text"]["text"])
