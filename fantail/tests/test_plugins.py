"""
This module tests the plugins located in `fantail.plugins`.
Each test is wrapped in a try/catch block to ensure the test is only run
if the dependencies are loaded.
"""

import importlib
import pytest

from fantail.plugins.registry import *

def test_plugin_registration(caplog):
    """
    Test plugin registration and error handling using a custom function.
    """

    r = PluginRegistry()

    # A dummy function to register that does nothing
    def dummy_func():
        pass

    # Test no `plugin_type` attribute
    with pytest.raises(PluginRegisterException):
        r.register(dummy_func)

    # Test unknown plugin type
    dummy_func.plugin_type = 'foo'
    with pytest.raises(PluginRegisterException):
        r.register(dummy_func)

    # Valid registration
    dummy_func.plugin_type = 'filter'
    r.register(dummy_func)
    assert 'Registered new plugin `dummy_func`' in caplog.text()

    assert type(r) == PluginRegistry
    assert len(r._plugins) == 1
    assert type(r.filters) == set
    assert len(r.filters) == 1
    assert list(r.filters)[0] == dummy_func

    # satisfy coverage
    assert list(r.filters)[0]() is None

def test_load_plugins_func(caplog):
    """
    Tests the load_plugins() function.
    """

    r = load_plugins()
    assert len(r._plugins) >= 1
    assert len(r.filters) >= 1
    assert 'Imported plugin module `fantail.plugins.plugin_test`' in caplog.text()
    assert 'Registered new plugin `register_test_filter` of type filter' in caplog.text()

def test_plugin_test_filter():
    """
    Tests that the pre-packaged plugin `plugin_test` returns correctly.
    """

    s = 'This is a string to be passed to a content filter'

    from fantail.plugins.plugin_test import register_test_filter
    r = PluginRegistry()
    r.register(register_test_filter)

    assert len(r.filters) == 1
    ret = list(r.filters)[0](s)
    assert ret == s
