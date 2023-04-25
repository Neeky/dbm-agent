# -*- encoding: utf-8 -*-

"""测试 orch 的安装逻辑"""

from pathlib import Path
from dbma.components.orchestrator.install import get_orch_version


def test_get_orch_version_given_2_3_6_pkg_then_return_2_3_6():
    expect = "2.3.6"
    pkg = Path("/usr/local/dbm-agent/pkgs/orchestrator-2.3.6-linux-amd64.tar.gz")
    assert get_orch_version(pkg) == expect


def test_get_orch_version_given_None_then_raise():
    pass
