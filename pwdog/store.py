# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Patrick Otto <patrick.otto@mayflower.de>
#                    Franz Pletz <franz.pletz@mayflower.de>
#
# This file is part of pwdog.
#
# pwdog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pwdog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pwdog.  If not, see <http://www.gnu.org/licenses/>.

import os
import os.path

class FilesystemStore(object):
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def __str__(self):
        return 'Cache(%s)' % self.cache_path

    def set(self, name, type, content):
        path = os.path.join(self.cache_path, name)
        try:
            os.makedirs(path)
        except:
            pass # meh

        file(os.path.join(path, type), 'w').write(content)

    def get(self, name=None, type=None):
        path = self.cache_path
        if name is not None:
            path = os.path.join(path, name)

        try:
            if type is None:
                return os.listdir(path)

            return file(os.path.join(path, type), 'r').read()
        except (OSError, IOError):
            return None

    def delete(self, name, type):
        namepath = os.path.join(self.cache_path, name)
        os.unlink(os.path.join(namepath, type))

        if len(os.listdir(namepath)) == 0:
            os.rmdir(namepath)

