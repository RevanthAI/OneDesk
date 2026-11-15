"""Compatibility import; canonical package: src.v2_1."""
import importlib
import sys
sys.modules[__name__] = importlib.import_module("src.v2_1")
