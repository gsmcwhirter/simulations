#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name='simulations',
    version='0.4.0',
    packages=[
        'simulations',
        'simulations.utils',
        'simulations.dynamics'
    ],
    package_dir={
        '': 'src',
    },
    install_requires=[
        'distribute',
        'numpy>=1.5',
        'pp'
    ],
    dependency_links=["https://www.ideafreemonoid.org/pip"],
    test_suite='nose.collector',
    tests_require=['nose'],
    author='Gregory McWhirter',
    author_email='gmcwhirt@uci.edu',
    description='A framework for evolutionary game theory simulations',
    url='https://www.github.com/gsmcwhirter/gametheory',
    license='MIT'
)
