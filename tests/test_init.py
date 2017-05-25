import pytest
from dapsenv.__init__ import main, execute
from dapsenv.exceptions import InvalidActionException
from dapsenv.exitcodes import E_INVALID_CLI, E_NO_IMPLEMENTATION_FOUND


# it fails when no sub-command/action was specified
def test_main():
    with pytest.raises(SystemExit) as error:
        main([""])
    assert error.value.code == E_INVALID_CLI


# it fails if an action is not implemented
def test_action_not_implemented():
    with pytest.raises(SystemExit) as error:
        execute({ "action": "test123" })

    assert error.value.code == E_NO_IMPLEMENTATION_FOUND
