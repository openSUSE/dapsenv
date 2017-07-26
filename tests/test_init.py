import pytest
from dapsenv import main, execute, configmanager
from dapsenv.exceptions import InvalidActionException
from dapsenv.exitcodes import E_INVALID_CLI, E_NO_IMPLEMENTATION_FOUND

def getprop(prop, config_type="", config_path="", default=None):
    return "0"

# it fails when no sub-command/action was specified
def test_main(monkeypatch):
    monkeypatch.setattr(configmanager, 'get_prop', getprop)
    with pytest.raises(SystemExit) as error:
        main([""])
    assert error.value.code == E_INVALID_CLI


# it fails if an action is not implemented
def test_action_not_implemented(monkeypatch):
    monkeypatch.setattr(configmanager, 'get_prop', getprop)
    with pytest.raises(SystemExit) as error:
        execute({"action": "test123"})

    assert error.value.code == E_NO_IMPLEMENTATION_FOUND
