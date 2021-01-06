#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from free_game_notifier.feed.steam import Feed, Item, steam_ratings

# Solitairica only has "All Reviews"
# Last Light Redux has "All" and "Recent" reviews.


def test_solitairica(solitairica):
    """Solitairica only has All Reviews"""
    item = Item.from_rss_element(solitairica)
    item.steam_store_link = "tests/steam/files/solitairica.html"
    with open(item.steam_store_link) as fh:
        html = fh.read()

    ratings = steam_ratings(html)
    assert ratings["overall"]
    assert not ratings["recent"]


def test_last_light(last_light):
    """Last Light has both reviews"""
    item = Item.from_rss_element(last_light)
    item.steam_store_link = "tests/steam/files/last_light.html"
    with open(item.steam_store_link) as fh:
        html = fh.read()

    ratings = steam_ratings(html)
    assert ratings["overall"]
    assert ratings["recent"]
