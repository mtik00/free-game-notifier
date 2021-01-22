#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
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
icons:
    custom_steam: https://custom.store.steampowered.com/favicon.ico
    test_steam: https://store.steampowered.com/favicon.ico
"""

@pytest.fixture
def configuration(monkeypatch):
    app_configuration.load_config(config_yaml)
    return app_configuration
