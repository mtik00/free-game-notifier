#!/usr/bin/env python3

import logging

import typer

from .cache import cache
from .feed import feed_factory
from .logger import get_logger
from .notifier import notifier_factory
from .settings import settings

LOGGER = get_logger()


def process_notifier(cache_key, notifier, item):
    sent = notifier.send(item)

    if sent:
        cache.add(cache_key, item.to_dict())
        cache.save()


def process_all_notifiers(item):
    # Compare the registered notifiers to the settings.  Ignore any notifiers
    # that aren't in both locations.
    notifier_factory_names = set(notifier_factory.keys())
    notifier_settings_names = set(settings["notifiers"].keys())
    notifier_names = notifier_factory_names & notifier_settings_names

    for name in notifier_names:
        urls = settings["notifiers"][name]

        if not urls:
            continue

        for url in urls:
            # Make the cache item specific to this particular item, which needs
            # to include the URL.  This way each "notifier/url/item" combo gets
            # its own cached value.
            cache_key = cache.get_key(item.title, item.posted, name, url)

            if cache_key in cache:
                LOGGER.debug("...%s already send to %s", item.title, url)
                continue

            notifier_class = notifier_factory[name]
            notifier = notifier_class(url=url)
            process_notifier(cache_key, notifier, item)


def process_feed(name, feed_class, url):
    """Process a single feed."""
    feed = feed_class(url=url)
    item = feed.get(index=0)

    if not item:
        LOGGER.warn("No items found in %s", url)
        return

    LOGGER.debug(f"found {item.title}")

    process_all_notifiers(item)


def process_all_feeds():
    """Find all registered feeds and process them if settings exist for it."""

    # Compare the registered feeds to the settings.  Ignore any feeds that aren't
    # in both locations.
    feed_factory_names = set(feed_factory.keys())
    feed_settings_names = set(settings["feeds"].keys())

    feed_names = feed_factory_names & feed_settings_names

    for name in feed_names:
        feed_class = feed_factory[name]
        for url in settings["feeds"][name]:
            process_feed(name, feed_class, url)


def main(
    settings_path: str = typer.Option(..., envvar="SFN_APP_SETTINGS_PATH"),
    debug: bool = typer.Option(False, envvar="SFN_APP_DEBUG"),
):
    settings.configure(settings_path)

    if debug or settings["debug"]:
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug("Loaded settings from %s", settings_path)

    cache.configure(path=settings["cache_path"], age=settings["cache_age"])
    cache.invalidate()

    process_all_feeds()


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
