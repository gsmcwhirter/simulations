#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
from setuptools import Extension

setup(
    name='simulations',
    version='0.8.3',
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
    ext_modules=[
        Extension("simulations.dynamics.replicator_fastfuncs",
                    sources=["src/simulations/dynamics/replicator_fastfuncs.c"],
                    include_dirs=["/usr/lib/python2.7/dist-packages/numpy/core/include/", 
                                  "/usr/lib/python2.6/dist-packages/numpy/core/include/",
                                  "/home/travis/virtualenv/python2.7/lib/python2.7/site-packages/numpy/core/include/",
                                  "/home/travis/virtualenv/python2.6/lib/python2.6/site-packages/numpy/core/include/"])
    ],
    package_dir={
        '': 'src',
    },
    install_requires=[
        'numpy>=1.5',
    ],
    tests_require=[
        'nose>=1.0'
    ],
    test_suite='nose.collector'
)
