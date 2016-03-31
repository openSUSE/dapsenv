import pytest
from dapsenv.argparser import ArgParser
from dapsenv.exitcodes import E_INVALID_CLI
from dapsenv.general import __version__

# it exits with exit code 2 if an invalid action/sub-command was specified
def test_parse_exception():
    code = 0

    try:
        argparser = ArgParser(["test", "abc", "123"])
        parsed_args = argparser.parse()
    except SystemExit as e:
        code = e.code

    assert code == E_INVALID_CLI

# it succeeds if a valid command was parsed to the command line
def test_parse_success():
    code = 0

    try:
        argparser = ArgParser(["config", "--global", "--property", "test"])
        parsed_args = argparser.parse()
    except SystemExit as e:
        code = e.code

    assert code == 0

# it returns the correct version number
def test_return_version(capsys):
    try:
        argparser = ArgParser(["--version"])
        parsed_args = argparser.parse()
    except SystemExit:
        pass

    out, err = capsys.readouterr()

    assert out == "DAPS Build Environment Version {}\n".format(__version__)
