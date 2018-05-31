#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name =          'isitanime_scrapy',
    version =       '1.0',
    packages =      find_packages(),
    zip_safe =      False,
    entry_points =  {'scrapy': ['settings = isitanime_scrapy.settings']},
)
