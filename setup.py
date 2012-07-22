#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(name='HAL',
      version='0.0.1',
      description='Powerful AI Framework',
      author='Xiaomao Chen',
      author_email='xiaomao5@live.com',
      url='http://dev.halbot.co.cc/',
      packages=['HAL', 'HAL.engine'],
      install_requires=['stemming'],
     )