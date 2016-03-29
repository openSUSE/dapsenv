import pytest
from dapsenv.__init__ import main
from dapsenv.exitcodes import E_INVALID_CLI

# it fails when no sub-command/action was specified
def test_main():
    code = 0

    try:
        main([""])
    except SystemExit as e:
        code = e.code

    assert code == E_INVALID_CLI
