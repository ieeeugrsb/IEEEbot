#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='IEEEbot',
      version='0.3',
      description='IEEE Telegram bot',
      author='IEEE Student Branch of Granada',
      author_email='ieeegranada@ieee.org',
      url='https://github.com/ieeeugrsb/IEEEbot',
      packages=find_packages(),
      license='GPL3',
      keywords='tools',
      install_requires=['pyTelegramBotAPI', 'Flask>=0.7.2'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv2)',
      ]
      )
