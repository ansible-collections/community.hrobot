# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import json
import pytest

from mock import MagicMock
from ansible_collections.community.hrobot.plugins.module_utils import robot
from ansible_collections.community.hrobot.plugins.module_utils import failover


class ModuleFailException(Exception):
    def __init__(self, msg, **kwargs):
        super(ModuleFailException, self).__init__(msg)
        self.fail_msg = msg
        self.fail_kwargs = kwargs


def get_module_mock():
    def f(msg, **kwargs):
        raise ModuleFailException(msg, **kwargs)

    module = MagicMock()
    module.fail_json = f
    module.from_json = json.loads
    return module


# ########################################################################################

GET_FAILOVER_SUCCESS = [
    (
        '1.2.3.4',
        (None, dict(
            body=json.dumps(dict(
                failover=dict(
                    active_server_ip='1.1.1.1',
                    ip='1.2.3.4',
                    netmask='255.255.255.255',
                )
            )).encode('utf-8'),
        )),
        '1.1.1.1',
        dict(
            active_server_ip='1.1.1.1',
            ip='1.2.3.4',
            netmask='255.255.255.255',
        )
    ),
]


GET_FAILOVER_FAIL = [
    (
        '1.2.3.4',
        (None, dict(
            body=json.dumps(dict(
                error=dict(
                    code="foo",
                    status=400,
                    message="bar",
                ),
            )).encode('utf-8'),
        )),
        'Request failed: 400 foo (bar)'
    ),
    (
        '1.2.3.4',
        (None, dict(
            body='{"foo": "bar"}'.encode('utf-8'),
        )),
        'Cannot interpret result: {"foo": "bar"}'
    ),
]


@pytest.mark.parametrize("ip, return_value, result, record", GET_FAILOVER_SUCCESS)
def test_get_failover_record(monkeypatch, ip, return_value, result, record):
    module = get_module_mock()
    robot.fetch_url = MagicMock(return_value=copy.deepcopy(return_value))

    assert failover.get_failover_record(module, ip) == record


@pytest.mark.parametrize("ip, return_value, result", GET_FAILOVER_FAIL)
def test_get_failover_record_fail(monkeypatch, ip, return_value, result):
    module = get_module_mock()
    robot.fetch_url = MagicMock(return_value=copy.deepcopy(return_value))

    with pytest.raises(ModuleFailException) as exc:
        failover.get_failover_record(module, ip)

    assert exc.value.fail_msg == result
    assert exc.value.fail_kwargs == dict()


@pytest.mark.parametrize("ip, return_value, result, record", GET_FAILOVER_SUCCESS)
def test_get_failover(monkeypatch, ip, return_value, result, record):
    module = get_module_mock()
    robot.fetch_url = MagicMock(return_value=copy.deepcopy(return_value))

    assert failover.get_failover(module, ip) == result


@pytest.mark.parametrize("ip, return_value, result", GET_FAILOVER_FAIL)
def test_get_failover_fail(monkeypatch, ip, return_value, result):
    module = get_module_mock()
    robot.fetch_url = MagicMock(return_value=copy.deepcopy(return_value))

    with pytest.raises(ModuleFailException) as exc:
        failover.get_failover(module, ip)

    assert exc.value.fail_msg == result
    assert exc.value.fail_kwargs == dict()


# ########################################################################################

SET_FAILOVER_SUCCESS = [
    (
        '1.2.3.4',
        '1.1.1.1',
        (None, dict(
            body=json.dumps(dict(
                failover=dict(
                    active_server_ip='1.1.1.2',
                )
            )).encode('utf-8'),
        )),
        ('1.1.1.2', True)
    ),
    (
        '1.2.3.4',
        '1.1.1.1',
        (None, dict(
            body=json.dumps(dict(
                error=dict(
                    code="FAILOVER_ALREADY_ROUTED",
                    status=400,
                    message="Failover already routed",
                ),
            )).encode('utf-8'),
        )),
        ('1.1.1.1', False)
    ),
]


SET_FAILOVER_FAIL = [
    (
        '1.2.3.4',
        '1.1.1.1',
        (None, dict(
            body=json.dumps(dict(
                error=dict(
                    code="foo",
                    status=400,
                    message="bar",
                ),
            )).encode('utf-8'),
        )),
        'Request failed: 400 foo (bar)'
    ),
]


@pytest.mark.parametrize("ip, value, return_value, result", SET_FAILOVER_SUCCESS)
def test_set_failover(monkeypatch, ip, value, return_value, result):
    module = get_module_mock()
    robot.fetch_url = MagicMock(return_value=copy.deepcopy(return_value))

    assert failover.set_failover(module, ip, value) == result


@pytest.mark.parametrize("ip, value, return_value, result", SET_FAILOVER_FAIL)
def test_set_failover_fail(monkeypatch, ip, value, return_value, result):
    module = get_module_mock()
    robot.fetch_url = MagicMock(return_value=copy.deepcopy(return_value))

    with pytest.raises(ModuleFailException) as exc:
        failover.set_failover(module, ip, value)

    assert exc.value.fail_msg == result
    assert exc.value.fail_kwargs == dict()
