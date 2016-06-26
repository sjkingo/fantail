"""
Tests for cli.py - the command line interface.
This does not test the functionality, merely the interface in cli.py.
See `test_staticsite.py` for functionality tests.
"""

from os import linesep
import pytest

from fantail.cli import main as fantail_main

def test_cli_noargs(capsys):
    """
    $ fantail
    """
    args = []
    with pytest.raises(SystemExit):
        fantail_main(args)
    stdout, stderr = capsys.readouterr()
    assert stdout.startswith('usage:')

def test_cli_help(capsys):
    """
    $ fantail --help
    """
    args = ['--help']
    with pytest.raises(SystemExit):
        fantail_main(args)
    stdout, stderr = capsys.readouterr()
    assert stdout.startswith('usage:')

def test_cli_init(capsys, tmpdir):
    """
    $ fantail init
    """
    path = str(tmpdir.join('test-site'))
    args = ['init', path]
    fantail_main(args)
    stdout, stderr = capsys.readouterr()
    assert stdout == 'Created new site at ' + path + linesep

def test_cli_init_existing(capsys, tmpdir, caplog):
    """
    $ fantail init
    $ fantail init
    """
    path = str(tmpdir.join('test-site'))
    args = ['init', path]
    test_cli_init(capsys, tmpdir) # succeeds
    with pytest.raises(SystemExit):
        fantail_main(args) # fails
    assert 'Site at ' + path + ' already exists.' in caplog.text()

def test_cli_build_site_does_not_exist(tmpdir, caplog):
    """
    $ fantail build
    """
    path = str(tmpdir.join('test-site'))
    args = ['build', path]
    with pytest.raises(SystemExit):
        fantail_main(args) # fails
    assert 'Site at ' + path + ' does not exist.' in caplog.text()

def test_cli_clean_site_does_not_exist(tmpdir, caplog):
    """
    $ fantail clean
    """
    path = str(tmpdir.join('test-site'))
    args = ['clean', path]
    with pytest.raises(SystemExit):
        fantail_main(args) # fails
    assert 'Site at ' + path + ' does not exist.' in caplog.text()
