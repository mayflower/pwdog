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

import ConfigParser

class Config(object):
    def __init__(self, filename, context):
        self.context = context
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(filename)

    def __getitem__(self, key):
	return self.get(key)

    def get(self, key):
        try:
            return self.parser.get(self.context, key)
        except ConfigParser.NoOptionError:
            try:
                return self.parser.get('common', key)
            except ConfigParser.NoOptionError:
                return None

