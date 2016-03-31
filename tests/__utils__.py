import os
import pytest

def make_tmp_file(existing_file, tmpdir):
    file_handle = tmpdir.join(existing_file)

    content = ""
    test_data = "{}/data".format(os.path.dirname(os.path.realpath(__file__)))

    with open("{}/{}".format(test_data, existing_file)) as f:
        content = f.read()

    file_handle.write(content)
    return file_handle
