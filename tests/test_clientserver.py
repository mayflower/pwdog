import json
from nose import with_setup

import pwdog.server as server
import pwdog.client as client

request_body = None

def setup_func():
    def _request(path, method, body=''):
        global request_body
        try:
            return None, request_body
        finally:
            request_body = body

    client._request = client.request
    client.request = _request

    server.setup('tests/pwdog.conf')
    client.setup('tests/pwdog.conf')
    server.store.set('foo', 'bar', 'test')

    assert server.store.get('foo', 'bar') == 'test'

def teardown_func():
    global request_body
    request_body = None
    client.request = client._request

    server.store.delete('foo', 'bar')
    assert server.store.get('foo', 'bar') is None

@with_setup(setup_func, teardown_func)
def test_credential_names():
    assert json.loads(server.credential_names()) == ['foo']

@with_setup(setup_func, teardown_func)
def test_credential_types():
    assert json.loads(server.credential_types('foo')) == ['bar']

@with_setup(setup_func, teardown_func)
def test_credential():
    assert server.credential('foo', 'bar') == 'test'

@with_setup(setup_func, teardown_func)
def test_credential_put_get_delete():
    client._credential_set('foo', 'baz', [client.config['mykeyid']], 'test')
    server.credential_put('foo', 'baz', request_body)

    assert client._credential_get('foo', 'baz')[3] == 'test'

    client.credential_delete('foo', 'baz')
    server.credential_delete('foo', 'baz', request_body)
    assert server.store.get('foo', 'baz') is None
