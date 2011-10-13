#!/usr/bin/env python

import sys
import argparse
import httplib2
import json
import difflib

import gpg
import cache

from pprint import pprint

gpg     = gpg.GPG()
cache   = cache.Cache('./.pwdog/localhost')

signee = ['patrick.otto@mayflower.de']

def request(path, method='GET', body=''):
    h = httplib2.Http()
    resp, content = h.request("http://127.0.0.1:8080%s" % path, method=method, body=body)
    if resp.status != 200:
        raise OSError
        
    return resp, content

def credential_get(name, type, **kwargs):
    try:
        resp, content = request('/credential/%s/%s' % (name, type), 'GET')
    except:
        print 'Could not fetch credential from server'
        return False
    
    try:
        cached_content = cache.read(name, type)
        
        recipients_cached = '\n'.join(map(str, gpg.get_cipher_recipients(cached_content)))
        recipients_remote = '\n'.join(map(str, gpg.get_cipher_recipients(content)))
        
        differ          = difflib.Differ()
        recipients_diff = list(differ.compare(recipients_cached.splitlines(), recipients_remote.splitlines()))
        
        for line in map(str, recipients_diff):
            if (line[0] + line[1]) == '+ ' or (line[0] + line[1]) == '- ':
                print '\n'.join(map(str, recipients_diff))
                
                sys.stdout.write('Accept? (y/N) ')
                reply = sys.stdin.readline().strip()
    
                if reply == 'y':
                    cache.write(name, type, content)
                else:
                    print "Operation aborted"
                    return False
    except:
        pass
    
    print '\n'.join(map(str, gpg.get_cipher_recipients(content)))
    print '\n' + gpg.decrypt(content)
        
    if cache.write(name, type, content) == True:
        print "Credential cached"
    else:
        print "Failed to cache credential"

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

def credential_delete(name, type):
    signed_cipher = gpg.sign(signee, 'DELETE %s/%s')
    
    request('/credential/%s/%s' % (name, type), 'DELETE', signed_cipher)

def credential_recipients(name, type):
    try:
        content = cache.read(name, type)
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
