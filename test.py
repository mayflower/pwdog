#!/usr/bin/env python

import nose
import sys

nose.run(argv=sys.argv + ['--with-coverage', '--cover-package=pwdog'])
