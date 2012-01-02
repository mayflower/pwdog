import pwdog.config as config

def test_config_server():
    conf = config.Config('doc/pwdog.conf', 'server')
    assert conf.get('store') == 'filesystem'

def test_config_client():
    conf = config.Config('doc/pwdog.conf', 'client')
    assert conf.get('cache_path') == './.pwdog/cache'
