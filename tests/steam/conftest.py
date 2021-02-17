#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from free_game_notifier.feed.steam import Feed


@pytest.fixture
def feed(configuration):
    return Feed(url="tests/steam/files/test-feed.xml")


@pytest.fixture
def solitairica(feed, configuration):
    return next((x for x in feed._feed["items"] if "solitairica" in x["title"].lower()))


@pytest.fixture
def last_light(feed, configuration):
    return next((x for x in feed._feed["items"] if "last light" in x["title"].lower()))


@pytest.fixture
def big_fish(feed, configuration):
    return next((x for x in feed._feed["items"] if "big fish" in x["title"].lower()))


@pytest.fixture
def assassins_creed(feed, configuration):
    return next(
        (
            x
            for x in feed._feed["items"]
            if "assassin's creed chronicles" in x["title"].lower()
        )
    )
