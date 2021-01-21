#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import requests
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
def mock_request(monkeypatch):
    def mock_get():
        return True

    def mock_raise():
        pass

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests.Response, "raise_for_status", mock_raise)


@pytest.fixture
def mock_request_raise(monkeypatch):
    def mock_get(*args, **kwargs):
        r = requests.Response()
        r.status_code = 404
        return r

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def configuration(monkeypatch):
    app_configuration.load_config(config_yaml)
    return app_configuration
