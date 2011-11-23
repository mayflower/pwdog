#!/usr/bin/env python

import bottle
import os
import json
from gpg import GPG
from store import FilesystemStore

store = FilesystemStore('./credentials')

def jsonify(f):
    def ret(*args, **kwargs):
        return json.dumps(f(*args, **kwargs)) + '\n'
    
    return ret

@bottle.get('/credential')
@jsonify
def credential_types():
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
def credential_put(name, type):
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

    print 'Old:',  map(str, old_recipients)
    print 'New:', map(str, new_recipients)

    if len(old_recipients) > 0 and signee not in old_recipients:
        raise bottle.HTTPResponse(status=401, output='No access')
    elif signee not in new_recipients:
        raise bottle.HTTPResponse(status=400, output='Idiot...')
    
    store.set(name, type, body)
        

@bottle.delete('/credential/:name/:type')
@jsonify
def credential_delete(name, type):
    body = bottle.request.body.read()
    gpg = GPG()

    signees = gpg.get_cipher_signees(body)
    credential = signees.next()

    for signee in signees:
        try:
            old_recipients = list(gpg.get_cipher_recipients(
                                file('credentials/%s/%s' % (name, type), 'r').read()
                                ))
        except:
            old_recipients = []

        print signee

        if len(old_recipients) > 0:
            if signee in old_recipients:
                store.delete(name, type)
            else:
                raise bottle.HTTPResponse(status=401)
        else:
            raise bottle.HTTPResponse(status=404)

bottle.debug(True)
bottle.run(host='localhost', port=8080)
