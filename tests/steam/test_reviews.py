#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from free_game_notifier.feed.steam import Feed, Item, steam_app_rating

# Solitairica only has "All Reviews"
# Last Light Redux has "All" and "Recent" reviews.


def test_solitairica(solitairica):
    """Solitairica only has All Reviews"""
    item = Item.from_rss_element(solitairica)
    item.steam_store_link = "tests/steam/files/solitairica.html"
    with open(item.steam_store_link) as fh:
        html = fh.read()

    rating = steam_app_rating(html)
    assert rating


def test_last_lighta(last_light):
    """Last Light has both reviews"""
    item = Item.from_rss_element(last_light)
    item.steam_store_link = "tests/steam/files/last-light-redux.html"
    with open(item.steam_store_link) as fh:
        html = fh.read()

    rating = steam_app_rating(html)
    assert rating


def test_big_fish(big_fish):
    """Big Fish has no steam store page"""
    pass
