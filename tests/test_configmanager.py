import dapsenv.configmanager as configmanager
import os.path
import pytest
from mock import patch

test_data_dir = "{}/data".format(os.path.dirname(os.path.realpath(__file__)))

# it returns a value of a property from a configuration file
input_data = [
    (
        "own",
        "{}/own-config.conf".format(test_data_dir),
        "test",
        "some cool text"
    ),
    (
        "global",
        "{}/global-config.conf".format(test_data_dir),
        "prop",
        "my cool value"
    ),
    (
        "user",
        "{}/user-config.conf".format(test_data_dir),
        "abc",
        "def"
    ),
]

@patch("dapsenv.configmanager.get_global_config_path")
@patch("dapsenv.configmanager.get_user_config_path")
@pytest.mark.parametrize("config_type,config_path,prop,expect", input_data)
def test_get(mock_get_user_config_path, mock_get_global_config_path, config_type, config_path,
    prop, expect):

    mock_get_global_config_path.return_value = config_path
    mock_get_user_config_path.return_value = config_path

    value = configmanager.get(prop, config_type, config_path)
    assert value == expect

# it returns the correct paths for all 3 types of config files
input_data = [
    (
        "own",
        "/tmp/something/bla.conf",
        "/tmp/something/bla.conf"
    ),
    (
        "user",
        "",
        "{}/.dapsenv/dapsenv.conf".format(os.path.expanduser("~")),
    ),
    (
        "global",
        "",
        "/etc/dapsenv/dapsenv.conf"
    )
]

@pytest.mark.parametrize("config_type,config_path,expected_path", input_data)
def test_get_config_path(config_type,config_path,expected_path):
    assert configmanager.get_config_path(config_type,config_path) == expected_path

# it parses multiple config files and merges the content together
def test_parse_config():
    config_files = [
        "{}/merge-test1.conf".format(test_data_dir),
        "{}/merge-test2.conf".format(test_data_dir),
        "{}/merge-test3.conf".format(test_data_dir)
    ]

    expected = {
        "prop": "my cool value",
        "merge_test": "content2",
        "abc": "def",
        "test": "some cool text",
        "merge_test2": "content1"
    }

    assert configmanager.parse_config(config_files) == expected
