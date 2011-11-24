#!/usr/bin/env python

from distutils.core import setup

setup(name='pwdog',
      version='0.1',
      description='Secure Credential Management',
      author='Mayflower pwdog Team',
      author_email='pwdog@mayflower.de',
      license='GPLv3',
      url='https://github.com/mayflower/pwdog',
      packages=['pwdog'],
      py_modules=['pwdog.gpg', 'pwdog.store', 'pwdog.config'],
      scripts=['scripts/pwdog', 'scripts/pwdog-server'],
      data_files=[('/etc', ['pwdog.conf'])],
     )
