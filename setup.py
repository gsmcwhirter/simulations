#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name='simulations',
    version='0.6.7',
    author='Gregory McWhirter',
    author_email='gmcwhirt@uci.edu',
    description='A framework for evolutionary game theory simulations',
    url='https://www.github.com/gsmcwhirter/simulations',
    license='MIT',
    packages=[
        'simulations',
        'simulations.utils',
        'simulations.dynamics'
    ],
    package_dir={
        '': 'src',
    },
    install_requires=[
        'numpy>=1.5',
        #'pp'
    ],
    tests_require=[
        'nose>=1.0'
    ],
    test_suite='nose.collector'
)
