import pwdog.config as config

def test_config_server():
    conf = config.Config('doc/pwdog.conf', 'server')
    assert conf.get('store') == 'filesystem'

def test_config_client():
    conf = config.Config('doc/pwdog.conf', 'client')
    assert conf.get('cache_path') == './.pwdog/cache'

def test_config_common():
    conf = config.Config('tests/pwdog.conf', 'client')
    assert conf.get('gpg_home_dir') == 'tests/.gnupg'

def test_config_notfound():
    conf = config.Config('tests/pwdog.conf', 'client')
    assert conf['notfound'] is None

