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


@pytest.mark.parametrize('user_input,default,expected,msg', [
    ('foo', 'default', 'foo', colored(u"› INPUT [default]: ", 'green')),  # optional input
    ('', 'default', 'default', colored(u"› INPUT [default]: ", 'green')),  # optional input default
    ('foo', None, 'foo', colored(u"› INPUT: ", 'green'))  # required input (no default)
])
def test_get_input(mocker, capsys, user_input, default, expected, msg):
    mock = mocker.patch('six.moves')
    mock.input = mocker.MagicMock(return_value=user_input)
    data = get_input('INPUT', default)

    mock.input.assert_called_once_with()
    assert msg in capsys.readouterr().out
    assert expected == data


def test_get_required_input_waiting(mocker, capsys):
    mock = mocker.patch('six.moves')
    mock.input = mocker.MagicMock(side_effect=['', 'foo'])
    data = get_input('INPUT')
    output = capsys.readouterr().out

    mock.input.assert_any_call()
    assert colored(u"› INPUT: ", 'green') in output
    assert mock.input.call_count is 2
    assert 'Please specify a value' in output
    assert data == 'foo'
