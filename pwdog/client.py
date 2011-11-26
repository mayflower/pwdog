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

import sys
import argparse
import httplib2
import difflib

from pprint import pprint

import gpg
import store
import config

gpg     = gpg.GPG()
config  = config.Config('pwdog.conf', 'client')
cache   = store.FilesystemStore(config.get('cache_path'))

def request(path, method='GET', body=''):
    h = httplib2.Http()
    # TODO: Assemble path here
    resp, content = h.request("http://127.0.0.1:8080%s" % path, method=method, body=body)
    if resp.status != 200:
        print 'HTTP FAIL(%i): %s' % (resp.status, content)

    return resp, content

def credential_get(name, type, **kwargs):
    try:
        # TODO: fix enumeration (format string fnord)
        resp, content = request('/credential/%s/%s' % (name, type), 'GET')
    except:
        print 'Could not fetch credential from server'
        return False

    try:
        cached_content = cache.get(name, type)

        recipients_cached = '\n'.join(map(str, gpg.get_cipher_recipients(cached_content)))
        recipients_remote = '\n'.join(map(str, gpg.get_cipher_recipients(content)))

        differ          = difflib.Differ()
        recipients_diff = differ.compare(recipients_cached.splitlines(), recipients_remote.splitlines())

        for line in map(str, recipients_diff):
            if (line[0] + line[1]) == '+ ' or (line[0] + line[1]) == '- ':
                print '\n'.join(map(str, recipients_diff))

                sys.stdout.write('Accept? (y/N) ')
                reply = sys.stdin.readline().strip()

                if reply == 'y':
                    cache.set(name, type, content)
                else:
                    print "Operation aborted"
                    return False
    except:
        pass

    signees = gpg.get_cipher_signees(content)
    cipher = signees.next()

    print 'Last edited by: ' + ('\n'.join(map(str, signees)) or 'n/a')

    print 'Access list:\n' + '\n'.join(map(lambda x: '\t* ' + str(x), gpg.get_cipher_recipients(cipher)))

    try:
        print '\n' + gpg.decrypt(cipher)
    except:
        print 'You have no access to this credential!'
        sys.exit(1)

    cache.set(name, type, content)

def credential_set(name, type):
    inp = None
    recipients = []

    while 1:
        sys.stdout.write('Enter name of your recipient: ')
        inp = sys.stdin.readline().strip()
        if inp == '':
            break
        recipients.append(inp)

    sys.stdout.write('Enter the credentials:\n')
    plaintext = ''.join(sys.stdin.readlines())

    cipher = gpg.encrypt(recipients, plaintext)
    signed_cipher = gpg.sign([config.get('mykeyid')], cipher)

    request('/credential/%s/%s' % (name, type), 'PUT', signed_cipher)

def credential_delete(name, type):
    signed_cipher = gpg.sign([config.get('mykeyid')], 'DELETE %s/%s')

    request('/credential/%s/%s' % (name, type), 'DELETE', signed_cipher)

def credential_recipients(name, type):
    try:
        content = cache.get(name, type)
        print '\n'.join(map(str, gpg.get_cipher_recipients(content)))
    except:
        raise

def main():
    parser = argparse.ArgumentParser(description='pwdog')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    parser_get = subparsers.add_parser('get', help='get a credential')
    parser_get.add_argument('name', type=str, default='', nargs='?',
                       help='name of credential')
    parser_get.add_argument('type', type=str, default='', nargs='?',
                       help='type of service')

    parser_set = subparsers.add_parser('set', help='set a credential')
    parser_set.add_argument('name', type=str,
                       help='name of credential')
    parser_set.add_argument('type', type=str,
                       help='type of service')

    parser_delete = subparsers.add_parser('delete', help='delete a credential')
    parser_delete.add_argument('name', type=str,
                       help='name of credential')
    parser_delete.add_argument('type', type=str,
                       help='type of service')

    parser_recipients = subparsers.add_parser('recipients', help='show recipients of a cached credential')
    parser_recipients.add_argument('name', type=str,
                       help='name of credential')
    parser_recipients.add_argument('type', type=str,
                       help='type of service')

    args = parser.parse_args()
    command_args = locals()['parser_' + args.command].parse_args(sys.argv[2:])
    globals()['credential_' + args.command].__call__(**vars(command_args))

if __name__ == '__main__':
    main()
