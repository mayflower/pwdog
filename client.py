#!/usr/bin/env python

import sys
import gpg
import argparse
import httplib2
import json

gpg = gpg.GPG()
signee = ['franz.pletz@mayflower.de']

def request(path, method='GET', body=''):
    h = httplib2.Http()
    resp, content = h.request("http://127.0.0.1:8080%s" % path, method=method, body=body)
    if resp != 200:
        print content

    return resp, content


    resp, content = request('/credential/%s/%s' % (name, type), 'GET')
def credential_get(name, type, **kwargs):
    print gpg.decrypt(content)
    print '\n'.join(map(str, gpg.get_cipher_recipients(content)))

def credential_set(name, type):
    input = None
    recipients = []

    while 1:
        sys.stdout.write('Enter name of your recipient: ')
        input = sys.stdin.readline().strip()
        if input == '':
            break
        recipients.append(input)

    sys.stdout.write('Enter the credentials:\n')
    plaintext = ''.join(sys.stdin.readlines())

    cipher = gpg.encrypt(recipients, plaintext)
    signed_cipher = gpg.sign(signee, cipher)

    request('/credential/%s/%s' % (name, type), 'PUT', signed_cipher)

    if type == '':
        sys.stdout.write('This will delete ALL credentials for %s! Are you sure? (y/N)' % name)

def credential_delete(name, type):
    signed_cipher = gpg.sign(signee, 'DELETE %s/%s')

    request('/credential/%s/%s' % (name, type), 'DELETE', signed_cipher)


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

    args = parser.parse_args()
    command_args = locals()['parser_' + args.command].parse_args(sys.argv[2:])
    globals()[args.command].__call__(**vars(command_args))

    globals()['credential_' + args.command].__call__(**vars(command_args))
if __name__ == '__main__':
    main()

