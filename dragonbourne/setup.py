#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(
    name="Sample Project",
    version="0.0.1",
    author="Britt Gresham",
    author_email="",
    description=(""),
    license="MIT",
    install_requires=['pyyaml'],
    entry_points="""
    [console_scripts]
    sample_command=app:sample
    """,
)
