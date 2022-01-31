#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from free_game_notifier.feed.steam import Item
from datetime import datetime

def test_bigfish(solitairica):
    item = Item.from_rss_element(solitairica)
    item.steam_store_link = "tests/steam/files/solitairica.html"

    assert(item.good_through_datetime.year != datetime.now().year)
