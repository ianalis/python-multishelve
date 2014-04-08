#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "multishelve",
    version = "0.1dev",
    packages = find_packages("multishelve"),
    test_suite = "test_multishelve.MultishelveTest",
    tests_require = "mox"
)
