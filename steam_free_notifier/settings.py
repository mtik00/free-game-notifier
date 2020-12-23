#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module to keep the application settings.
"""
import os

LOCAL_TZ = (
    os.environ.get("SFN_APP_LOCAL_TIMEZONE", "UTC").replace('"', "").replace("'", "")
)
