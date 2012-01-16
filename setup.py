#!/usr/bin/env python

from setuptools import setup

setup (
    name = 'gametheory.base',
    version = '0.1',
    packages = [
        'gametheory',
        'gametheory.base'
    ],
    package_dir = {
        '': 'src',
    },
    install_requires = [
        'distribute',
        'numpy>=1.5'
    ],
    dependency_links = ["https://www.ideafreemonoid.org/pip"],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    author = 'Gregory McWhirter',
    author_email = 'gmcwhirt@uci.edu',
    description = 'A framework for evolutionary game theory simulations',
    url = 'https://www.github.com/gsmcwhirter/gametheory',
    license = 'MIT'
)
