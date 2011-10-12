#!/usr/bin/env python

import bottle
import os
import json
from gpg import GPG

def jsonify(f):
    def ret(*args, **kwargs):
        return json.dumps(f(*args, **kwargs))
    
    return ret

@bottle.get('/credential')
@jsonify
def credential_types():
    return os.listdir('credentials')

@bottle.get('/credential/:name')
@jsonify
def credential_types(name):
    return os.listdir('credentials/%s' % name)

@bottle.get('/credential/:name/:type')
def credential(name, type):
    try:
        return file('credentials/%s/%s' % (name, type)).read()
    except:
        raise bottle.HTTPResponse(status=404, output='%s/%s not found' % (name, type))


@bottle.put('/credential/:name/:type')
@jsonify
def credential_put(name, type):
    try:
        os.makedirs('credentials/%s' % name)
    except OSError:
        pass # trololo

    body = bottle.request.body.read()
    gpg = GPG()

    signees = gpg.get_cipher_signees(body)
    credential = signees.next()
    signee = signees.next()
    
    try:
        old_recipients = list(gpg.get_cipher_recipients(
                            file('credentials/%s/%s' % (name, type), 'r').read()
                        ))
    except:
        old_recipients = []

    new_recipients = list(gpg.get_cipher_recipients(credential))

    print map(str, old_recipients)
    print map(str, new_recipients)

    if len(old_recipients) > 0 and signee not in old_recipients:
        raise bottle.HTTPResponse(status=401, output='No access')
    elif signee not in new_recipients:
        raise bottle.HTTPResponse(status=400, output='Idiot...')
    else:
        file('credentials/%s/%s' % (name, type), 'w').write(credential)
        

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
                os.unlink('credentials/%s/%s' % (name, type))
            else:
                raise bottle.HTTPResponse(status=401)
        else:
            raise bottle.HTTPResponse(status=404)

bottle.debug(True)
bottle.run(host='localhost', port=8080)
