__author__="gmcwhirt"
__date__ ="$Sep 26, 2011 2:43:53 PM$"

from setuptools import setup, find_packages

setup (
  name = 'gametheory.base',
  version = '0.1',
  packages = find_packages('src'),
  package_dir = {
    '': 'src',
  },
  namespace_packages = ['gametheory'],
  author = 'Gregory McWhirter',
  author_email = 'gmcwhirt@uci.edu',
  description = 'Game theory simulations for escalation research',
  url = 'https://www.github.com/gsmcwhirter/gametheory',
  license = 'MIT',
  entry_points = {
    "console_scripts": [
    ]
  }
)
