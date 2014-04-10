#!/usr/bin/env python

from setuptools import setup

setup(
    name = "multishelve",
    version = "0.1dev",
    packages = ["multishelve"],
    test_suite = "test_multishelve.MultishelveTest",
    tests_require = "mox"
)
