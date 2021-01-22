#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import requests
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


@pytest.fixture(autouse=True)
def cache(monkeypatch):
    def mock_save():
        return True

    app_cache.configure()
    monkeypatch.setattr(app_cache, "save", mock_save)
    return app_cache


@pytest.fixture
def configuration(monkeypatch):
    app_configuration.load_config(config_yaml)
    return app_configuration


@pytest.fixture
def mock_request(monkeypatch):
    def mock_get(*args, **kwargs):
        r = requests.Response()
        r.status_code = 200
        return r

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_request_raise(monkeypatch):
    def mock_get(*args, **kwargs):
        r = requests.Response()
        r.status_code = 404
        return r

    monkeypatch.setattr(requests, "get", mock_get)
