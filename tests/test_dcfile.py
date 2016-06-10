import pytest
from dapsenv.exceptions import DCFileMAINNotFoundException
from dapsenv.dcfile import DCFile
from _pytest.runner import Failed
from __utils__ import make_tmp_file

data = [
    (
        "DC-suse-openstack-cloud-admin",
        "bk_openstack_admin.xml",
        None
    ),
    (
        "DC-suse-openstack-cloud-all",
        "MAIN.suse-openstack-cloud.xml",
        None
    ),
    (
        "DC-suse-openstack-cloud-deployment",
        "MAIN.suse-openstack-cloud.xml",
        "book.cloud.deploy"
    ),
    (
        "DC-suse-openstack-cloud-supplement",
        "book_cloud_suppl.xml",
        "book.cloud.suppl"
    ),
    (
        "DC-suse-openstack-cloud-user",
        "bk_openstack_user.xml",
        None
    )
]
@pytest.mark.parametrize("dcfile,expected_main,expected_rootid", data)
def test_tryparse(dcfile, expected_main, expected_rootid, tmpdir):
    test_file = make_tmp_file(dcfile, tmpdir)
    dc = None

    with pytest.raises(Failed):
        with pytest.raises(DCFileMAINNotFoundException):
            dc = DCFile(test_file.__str__())

    assert dc.main == expected_main
    assert dc.rootid == expected_rootid

data = [
    ("DC-error"), ("DC-error-2")
]
@pytest.mark.parametrize("dcfile", data)
def test_tryparse_fail(dcfile, tmpdir):
    test_file = make_tmp_file(dcfile, tmpdir)

    with pytest.raises(DCFileMAINNotFoundException):
        DCFile(test_file.__str__())
