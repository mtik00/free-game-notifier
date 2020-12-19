#!/usr/bin/env python3

import logging


def get_logger():
    logger = logging.getLogger("steam_free_notifier")
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %H:%M:%S %Z",
    )

    return logger
