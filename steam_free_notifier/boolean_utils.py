#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A module to hold utility functions for booleans."""


def to_bool(var):
    """Converts a variable to a boolean with some string interpretation.

    The object will be converted to a lowercase string and the first character
    will be tested.  `True` is returned when the first character is "1", "t", or "y".
    `False` will be returned in all other cases.
    """
    if not var:
        return False

    return str(var).lower()[0] in ["1", "t", "y"]
