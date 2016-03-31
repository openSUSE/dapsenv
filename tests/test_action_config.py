from dapsenv.actions.config import Config
from dapsenv.exitcodes import E_CONFIG_PROP_NOT_FOUND
from mock import patch

# it shows the correct property value on the command line
@patch("dapsenv.configmanager.get")
def test_get_property(get_mocking, capsys):
    args = {'global': True, 'property': 'test', 'action': 'config', 'user': False, 'value': None}
    expected = "abc"

    get_mocking.return_value = expected

    config_class = Config()
    config_class.execute(args)

    out, err = capsys.readouterr()
    assert out == "{}\n".format(expected) 

# it exits with exit code 4 if a property was not found
@patch("dapsenv.configmanager.get")
def test_get_property_exit_code(get_mocking, capsys):
    args = {'global': True, 'property': 'test', 'action': 'config', 'user': False, 'value': None}
    get_mocking.return_value = ""

    config_class = Config()
    code = 0

    try:
        config_class.execute(args)
    except SystemExit as e:
        code = e.code

    assert code == E_CONFIG_PROP_NOT_FOUND
