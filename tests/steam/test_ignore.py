#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from free_game_notifier.feed.steam import Feed

def test_bigfish(ignore_configuration, feed):
    items = feed.get_items(count=100)
    assert not any((x for x in items if "big fish" in x.title.lower()))
