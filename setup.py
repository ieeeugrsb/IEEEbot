#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='IEEEbot',
      version='0.4',
      description='IEEE Telegram bot',
      author='IEEE Student Branch of Granada',
      author_email='ieeegranada@ieee.org',
      url='https://github.com/ieeeugrsb/IEEEbot',
      packages=find_packages(),
      license='AGPLv3+',
      keywords='tools',
      install_requires=['pyTelegramBotAPI>=1.4.1', 'Flask>=0.7.2'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
      ]
      )
