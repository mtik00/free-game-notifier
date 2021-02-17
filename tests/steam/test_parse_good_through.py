#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from free_game_notifier.feed.steam import Item


def testassassins_creed(assassins_creed, monkeypatch):
    """Assassin's creed has an invalid Timezone: 'Local'"""
    item = Item.from_rss_element(assassins_creed)

    def mock_get_steam_store_html():
        return ""

    monkeypatch.setattr(item, "get_steam_store_html", mock_get_steam_store_html)
