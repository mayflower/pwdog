#!/usr/bin/env python

import sys
import gpg
import argparse
import httplib2
import json

gpg = gpg.GPG()
signee = 'codec@fnord.cx'

def request(path, method='GET', body=''):
    h = httplib2.Http()
    return h.request("http://127.0.0.1:8080%s" % path, method=method, body=body)


def get(name, type, **kwargs):
    if name != '':
        name = '/' + name
    if type != '':
        type = '/' + type

    resp, content = request('/credential%s%s' % (name, type), 'GET')
    print gpg.decrypt(content)

def set(name, type):
    # TODO: sign and push to server
    input = None
    recipients = []

    while input != '':
        sys.stdout.write('Enter name of your recipient: ')
        input = sys.stdin.readline().strip()
        recipients.append(input)

    sys.stdout.write('Enter the credentials:\n')
    plaintext = sys.stdin.readlines()

    cipher = gpg.encrypt(recipients, "".join(plaintext))
    signed_cipher = gpg.sign(['codec@fnord.cx'], cipher)

    request('/credential/%s/%s' % (name, type), 'PUT', signed_cipher)

def delete(name, type):
    if type == '':
        sys.stdout.write('This will delete ALL credentials for %s! Are you sure? (y/N)' % name)

    signed_cipher = gpg.sign([signee], 'DELETE %s/%s')

    request('/credential/%s/%s' % (name, type), 'DELETE', signed_cipher)

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

args = parser.parse_args()
command_args = locals()['parser_' + args.command].parse_args(sys.argv[2:])
locals()[args.command].__call__(**vars(command_args))

