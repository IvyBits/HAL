#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='HAL',
      version='0.0.3',
      description='Powerful AI Framework',
      long_description=long_description,
      author='Xiaomao Chen',
      author_email='xiaomao5@live.com',
      url='http://www.halbot.co.cc/',
      packages=['HAL', 'HAL.engine'],
      install_requires=['stemming'],
      entry_points={
        'console_scripts': [
            'hal = HAL.mainentry:main',
            'whal = HAL.tkgui:main',
        ],
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Chat',
          'Topic :: Education',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
          ],
     )