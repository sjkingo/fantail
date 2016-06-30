"""
Tests for staticsite.py - the static site generator
"""

import os.path
import pytest

from fantail.staticsite import StaticSite

def test_init(tmpdir, caplog):
    # Verify path does not exist
    path = str(tmpdir.join('test-site'))
    assert not os.path.isdir(path)

    # Create the site
    site = StaticSite(path)
    site.init_site()

    # Verify directories have been created
    assert path == site.path
    assert os.path.isdir(path)
    assert os.path.isdir(os.path.join(path, 'output', '.git'))

    assert 'Welcome from' in caplog.text()
    assert str(repr(site)) == '<StaticSite "' + path + '">'

def test_dir_properties(tmpdir):
    path = str(tmpdir.join('test-site'))
    site = StaticSite(path)
    assert site.template_dir == os.path.join(path, 'templates')
    assert site.pages_dir == os.path.join(path, 'pages')
    assert site.output_dir == os.path.join(path, 'output')

def test_site_clean(tmpdir, caplog):
    path = str(tmpdir.join('test-site'))
    site = StaticSite(path)

    # This should fail as init() was not called first
    with pytest.raises(SystemExit):
        site.clean_site()
    assert 'Site at ' + path + ' does not exist. Please' in caplog.text()

    site.init_site()
    # This should succeed now
    site.clean_site()
    assert 'Removed output directory from' in caplog.text()
