# -*- coding: utf-8 -*-
from experimentum.cli import print_failure, get_input
import pytest
from termcolor import colored


def test_print_failure(capsys):
    print_failure('My failure message')
    assert 'My failure message' in capsys.readouterr().err


def test_print_failure_with_exit(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        print_failure('My failure message', 2)
    assert 'My failure message' in capsys.readouterr().err
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2


def test_get_default_input(mocker):
    mock = mocker.patch('six.moves')
    mock.input = mocker.MagicMock(return_value='foo')
    data = get_input('INPUT', 'default')

    mock.input.assert_called_once_with(colored("› INPUT [default]: ", 'green'))
    assert data == 'foo'

def test_get_default_input_default(mocker):
    mock = mocker.patch('six.moves')
    mock.input = mocker.MagicMock(return_value='')
    data = get_input('INPUT', 'default')

    mock.input.assert_called_once_with(colored("› INPUT [default]: ", 'green'))
    assert data == 'default'

def test_get_required_input(mocker):
    mock = mocker.patch('six.moves')
    mock.input = mocker.MagicMock(return_value='foo')
    data = get_input('INPUT')

    mock.input.assert_called_once_with(colored("› INPUT: ", 'green'))
    assert data == 'foo'

def test_get_required_input_waiting(mocker, capsys):
    mock = mocker.patch('six.moves')
    mock.input = mocker.MagicMock(side_effect=['', 'foo'])
    data = get_input('INPUT')

    mock.input.assert_any_call(colored("› INPUT: ", 'green'))
    assert mock.input.call_count is 2
    assert 'Please specify a value' in capsys.readouterr().out
    assert data == 'foo'
