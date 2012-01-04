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

import bottle
import json
from gpg import GPG
import os
import os.path

from store import FilesystemStore
from config import Config

store = None
config = None

def jsonify(f):
    def ret(*args, **kwargs):
        return json.dumps(f(*args, **kwargs)) + '\n'

    return ret

@bottle.get('/credential')
@jsonify
def credential_names():
    return store.get()

@bottle.get('/credential/:name')
@jsonify
def credential_types(name):
    return store.get(name)

@bottle.get('/credential/:name/:type')
def credential(name, type):
    credential = store.get(name, type)
    if credential is None:
        raise bottle.HTTPResponse(status=404, output='%s/%s not found' % (name, type))
    else:
        return credential


@bottle.put('/credential/:name/:type')
@jsonify
def credential_put(name, type, body=None):
    if body is None:
        body = bottle.request.body.read()
    gpg = GPG()

    signees = gpg.get_cipher_signees(body)
    credential = signees.next()
    signee = signees.next()

    old_credential = store.get(name, type)
    if old_credential is None:
        old_recipients = []
    else:
        old_recipients = list(gpg.get_cipher_recipients(gpg.get_cipher_signees(old_credential).next()))

    new_recipients = list(gpg.get_cipher_recipients(credential))

    #print('Old:',  map(str, old_recipients))
    #print('New:', map(str, new_recipients))

    if len(old_recipients) > 0 and signee not in old_recipients:
        raise bottle.HTTPResponse(status=401, output='No access')
    elif signee not in new_recipients:
        raise bottle.HTTPResponse(status=400, output='Idiot...')

    store.set(name, type, body)


@bottle.delete('/credential/:name/:type')
@jsonify
def credential_delete(name, type, body=None):
    if body is None:
        body = bottle.request.body.read()
    gpg = GPG()

    signees = gpg.get_cipher_signees(body)
    signees.next()
    signees = list(signees)

    old_signees = gpg.get_cipher_signees(store.get(name, type))
    old_recipients = list(gpg.get_cipher_recipients(old_signees.next()))
    for signee in signees:
        if len(old_recipients) > 0:
            if signee in old_recipients:
                store.delete(name, type)
                return
            else:
                raise bottle.HTTPResponse(status=401)
        else:
            raise bottle.HTTPResponse(status=404)

def setup(configpath):
    global config
    config = Config(configpath, 'server')
    if config.get('store') == 'filesystem':
        global store
        store = FilesystemStore(config.get('store_path'))
    else:
        raise NotImplemented('Only filesystem store is currently implemented')


def main():
    setup(os.path.join(os.environ['HOME'], '.config/pwdog/pwdog.conf'))
    bottle.debug(True)
    bottle.run(host='localhost', port=8080)

if __name__ == '__main__':
    main()
