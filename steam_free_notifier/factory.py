#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ClassFactory:
    def __init__(self):
        self.mapping = {}

    def register(self, key, obj):
        self.mapping[key] = obj

    def get(self, key):
        if not (item := self.mapping.get(key)):
            raise ValueError(f"Unknown mapping: '{key}'")

        return item

    def keys(self):
        return self.mapping.keys()

    def values(self):
        return self.mapping.values()

    def items(self):
        return self.mapping.items()

    def __getitem__(self, key):
        return self.mapping.get(key)
