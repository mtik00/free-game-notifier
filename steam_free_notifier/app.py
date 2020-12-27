#!/usr/bin/env python3

import logging

import typer

from .cache import Cache
from .feed import feed_factory
from .logger import get_logger
from .notifier import notifier_factory
from .settings import get_settings

LOGGER = get_logger()


def process_feed(settings, cache, name, feed_class):
    """Process a single feed."""
    feed_url = (settings["feeds"].get(name) or {}).get("url")
    feed = feed_class(url=feed_url)
    item = feed.get(index=0)

    if not item:
        LOGGER.warn("No items found in %s", feed_url)
        return

    LOGGER.debug(f"found {item.title}")

    for notifier_name, notifier_class in notifier_factory.items():
        # Check the urls.  Default to `None` if none are defined so the
        # output is logged.
        urls = settings["notifiers"].get(notifier_name) or [{"url": None}]
        for url in urls:
            url = url["url"]  # TODO: This is stupid

            # Make the cache item specific to this particular item, which needs
            # to include the URL.  This way each "notifier/url/item" combo gets
            # its own cached value.
            cache_key = cache.get_key(item.title, item.posted, notifier_name, url)

            if cache_key in cache:
                LOGGER.debug("...%s already send to %s", item.title, url)
                continue

            notifier = notifier_class(url=url)
            sent = notifier.send(item)

            if sent:

                # TODO: Cache key needs to include the notifier somehow
                # i.e. we notified slack, but what about email?
                # should each notifier have a cache item, each feed item cache
                # which notifier, etc.
                cache.add(cache_key, item.to_dict())
                cache.save()


def process_all_feeds(settings, cache):
    """Find all registered feeds and process them if settings exist for it."""

    # Compare the registered feeds to the settings.  Ignore any feeds that aren't
    # in both locations.
    feed_factory_names = set(feed_factory.keys())
    feed_settings_names = set(settings["feeds"].keys())

    feed_names = feed_factory_names & feed_settings_names

    for name in feed_names:
        feed_class = feed_factory[name]
        process_feed(settings, cache, name, feed_class)


def main(
    settings_path: str = typer.Option(..., envvar="SFN_APP_SETTINGS_PATH"),
    debug: bool = typer.Option(False, envvar="SFN_APP_DEBUG"),
):
    settings = get_settings(settings_path)

    if debug or settings["debug"]:
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug("Loaded settings from %s", settings_path)

    cache = Cache(path=settings["cache_path"], age=settings["cache_age"])
    cache.invalidate()
    process_all_feeds(settings, cache)


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
