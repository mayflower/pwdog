#!/usr/bin/env python

from distutils.core import setup

setup(name='pwdog',
      version='0.1',
      description='Secure Credential Management',
      author='Franz Pletz',
      author_email='fpletz@fnordicwalking.de',
      url='http://git.mayflower.de',
      packages=['pwdog'],
      py_modules=['pwdog.gpg', 'pwdog.store', 'pwdog.config'],
      scripts=['scripts/pwdog', 'scripts/pwdog-server'],
     )
