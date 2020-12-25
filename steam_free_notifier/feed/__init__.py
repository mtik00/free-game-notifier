#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ..factory import ClassFactory
from .steam import Feed as SteamFeed

feed_factory = ClassFactory()
feed_factory.register("steam", SteamFeed)
