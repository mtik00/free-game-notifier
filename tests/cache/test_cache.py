#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from free_game_notifier.cache import cache
from free_game_notifier.feed.steam import Item

cache.configure()
item = Item(
    title="Test Title",
    summary="Test Summary",
    steam_link="https://steam.com/game/1.html",
    posted=time.time(),
    good_through=None,
    published=None,
)


def test_cache():
    notifier_name = "slack"
    notifier_url = "https://slackwebook/test"
    print(cache)
    cache_key = cache.get_key(item.title, item.posted, notifier_name, notifier_url)
    assert cache_key not in cache

    cache.add(cache_key, item.to_dict())
    assert cache_key in cache
