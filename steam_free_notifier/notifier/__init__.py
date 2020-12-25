#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ..factory import ClassFactory
from .slack import Notifier as SlackNotifier

notifier_factory = ClassFactory()
notifier_factory.register("slack", SlackNotifier)
