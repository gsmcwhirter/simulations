#!/usr/bin/env python

from distutils.core import setup

setup (
    name = 'gametheory.base',
    version = '0.1',
    packages = [
        'gametheory.base'
    ],
    package_dir = {
        '': 'src',
    },
    author = 'Gregory McWhirter',
    author_email = 'gmcwhirt@uci.edu',
    description = 'Game theory simulations: base package',
    url = 'https://www.github.com/gsmcwhirter/gametheory',
    license = 'MIT'
)
