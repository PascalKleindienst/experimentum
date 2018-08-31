from experimentum.cli import print_failure
import pytest


def test_print_failure(capsys):
    print_failure('My failure message')
    assert 'My failure message' in capsys.readouterr().err


def test_print_failure_with_exit(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        print_failure('My failure message', 2)
    assert 'My failure message' in capsys.readouterr().err
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
