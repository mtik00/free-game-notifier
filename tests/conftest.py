#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from free_game_notifier.cache import cache as app_cache
from free_game_notifier.config import configuration as app_configuration


config_yaml = """
---
timezone: "UTC"
cache_age: 30
start_date: 2020-12-01
feeds:
    steam:
        -
notifiers:
    slack:
        -
debug: false
"""


@pytest.fixture
def cache(monkeypatch):
    def mock_save():
        return True

    monkeypatch.setattr(app_cache, "save", mock_save)
    return app_cache


@pytest.fixture
def configuration(monkeypatch):
    app_configuration.load_config(config_yaml)
    return app_configuration
