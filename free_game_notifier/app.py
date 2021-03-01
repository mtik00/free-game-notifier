#!/usr/bin/env python3

import logging
from contextlib import contextmanager

import pendulum
import typer

from .cache import cache
from .config import configuration
from .feed import feed_factory
from .logger import set_root_level
from .notifier import notifier_factory

LOGGER = logging.getLogger(__name__)


def process_notifier(cache_key, notifier, item):
    sent = False

    try:
        sent = notifier.send(item)
    except Exception:
        LOGGER.error("Failed to send", exc_info=True)

    if sent:
        cache.add(cache_key, item.to_dict())
        cache.save()


def process_all_notifiers(item):
    # Compare the registered notifiers to the config.  Ignore any notifiers
    # that aren't in both locations.
    notifier_factory_names = set(notifier_factory.keys())
    notifier_config_names = set(configuration["notifiers"].keys())
    notifier_names = notifier_factory_names & notifier_config_names

    for notifier_name in notifier_names:
        # default to at least [None] so the notifier will dump to the log file
        notifier_urls = configuration["notifiers"][notifier_name] or [None]

        for notifier_url in notifier_urls:
            # Make the cache key specific to this particular item, which needs
            # to include the URL.  This way each "notifier/url/item" combo gets
            # its own cached value.
            cache_key = cache.get_key(item.title, notifier_name, notifier_url)

            if cache_key in cache:
                LOGGER.debug("...%s already sent to %s", item.title, notifier_url)
                continue

            notifier_class = notifier_factory[notifier_name]
            notifier = notifier_class(url=notifier_url)
            process_notifier(cache_key, notifier, item)


def process_feed(name, feed_class, url):
    """Process a single feed."""
    try:
        feed = feed_class(url=url)
        items = feed.get_items(count=10)
    except Exception:
        LOGGER.error("Could not parse %s", url, exc_info=True)
        return

    if not items:
        LOGGER.warning("No items found in %s", url)
        return

    for item in items:
        process_all_notifiers(item)


def process_all_feeds():
    """Find all registered feeds and process them if a configuration exists for it."""

    # Compare the registered feeds to the config.  Ignore any feeds that aren't
    # in both locations.
    feed_factory_names = set(feed_factory.keys())
    feed_config_names = set(configuration["feeds"].keys())

    feed_names = feed_factory_names & feed_config_names

    for name in feed_names:
        feed_class = feed_factory[name]
        for url in configuration["feeds"][name]:
            process_feed(name, feed_class, url)


def main(
    config_path: str = typer.Option(..., envvar="SFN_APP_CONFIG_PATH"),
    debug: bool = typer.Option(False, envvar="SFN_APP_DEBUG"),
    dry_run: bool = typer.Option(False),
):
    configuration.load_config(config_path)

    if debug:
        configuration["debug"] = True

    if configuration["debug"]:
        set_root_level(logging.DEBUG)

    configuration["dry-run"] = dry_run

    LOGGER.debug("Loaded configuration from %s", config_path)

    cache.configure(path=configuration["cache_path"], age=configuration["cache_age"])
    cache.invalidate()

    process_all_feeds()


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
