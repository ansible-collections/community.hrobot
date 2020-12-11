# Copyright (c), Felix Fontein <felix@fontein.de>, 2020
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json
import textwrap

import pytest

from mock import MagicMock

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.inventory.data import InventoryData
from ansible.inventory.manager import InventoryManager

from ansible_collections.community.internal_test_tools.tests.unit.mock.path import mock_unfrackpath_noop
from ansible_collections.community.internal_test_tools.tests.unit.mock.loader import DictDataLoader
from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
    OpenUrlCall,
    OpenUrlProxy,
)

from ansible_collections.community.hrobot.plugins.inventory.robot import InventoryModule
from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def get_option(option):
    if option == 'filters':
        return {}
    if option == 'hetzner_user':
        return 'test'
    if option == 'hetzner_password':
        return 'hunter2'
    return False


def test_populate(inventory, mocker):
    open_url = OpenUrlProxy([
        OpenUrlCall('GET', 200)
        .result_json([
            {
                'server': {
                    'server_ip': '1.2.3.4',
                },
            },
            {
                'server': {
                    'server_ip': '1.2.3.5',
                    'server_name': 'test-server',
                },
            },
        ])
        .expect_url('{0}/server'.format(BASE_URL)),
    ])
    mocker.patch('ansible_collections.community.hrobot.plugins.module_utils.robot.open_url', open_url)

    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory.populate(inventory.get_servers())

    open_url.assert_is_done()

    host_1 = inventory.inventory.get_host('1.2.3.4')
    host_2 = inventory.inventory.get_host('test-server')

    host_1_vars = host_1.get_vars()
    host_2_vars = host_2.get_vars()

    assert host_1_vars['ansible_host'] == '1.2.3.4'
    assert host_1_vars['hrobot_server_ip'] == '1.2.3.4'
    assert 'hrobot_server_name' not in host_1_vars
    assert host_2_vars['ansible_host'] == '1.2.3.5'
    assert host_2_vars['hrobot_server_ip'] == '1.2.3.5'
    assert host_2_vars['hrobot_server_name'] == 'test-server'


def test_inventory_file_simple(mocker):
    open_url = OpenUrlProxy([
        OpenUrlCall('GET', 200)
        .result_json([
            {
                'server': {
                    'server_ip': '1.2.3.4',
                    'dc': 'foo',
                },
            },
            {
                'server': {
                    'server_ip': '1.2.3.5',
                    'server_name': 'test-server',
                    'dc': 'foo',
                },
            },
            {
                'server': {
                    'server_ip': '1.2.3.6',
                    'server_name': 'test-server-2',
                    'dc': 'bar',
                },
            },
        ])
        .expect_url('{0}/server'.format(BASE_URL)),
    ])
    mocker.patch('ansible_collections.community.hrobot.plugins.module_utils.robot.open_url', open_url)
    mocker.patch('ansible.inventory.manager.unfrackpath', mock_unfrackpath_noop)
    mocker.patch('os.path.exists', lambda x: True)
    mocker.patch('os.access', lambda x, y: True)

    inventory_filename = "test.robot.yaml"
    C.INVENTORY_ENABLED = ['community.hrobot.robot']
    inventory_file = {inventory_filename: textwrap.dedent("""\
    ---
    plugin: community.hrobot.robot
    hetzner_user: test
    hetzner_password: hunter2
    filters:
      dc: foo
    """)}
    im = InventoryManager(loader=DictDataLoader(inventory_file), sources=inventory_filename)
    open_url.assert_is_done()

    assert im._inventory.hosts
    assert '1.2.3.4' in im._inventory.hosts
    assert 'test-server' in im._inventory.hosts
    assert 'test-server-2' not in im._inventory.hosts
    assert im._inventory.get_host('1.2.3.4') in im._inventory.groups['ungrouped'].hosts
    assert im._inventory.get_host('test-server') in im._inventory.groups['ungrouped'].hosts
    assert len(im._inventory.groups['ungrouped'].hosts) == 2
    assert len(im._inventory.groups['all'].hosts) == 0


@pytest.mark.parametrize("error_result", [
    None,
    json.dumps(dict(
        error=dict(
            code="foo",
            status=400,
            message="bar",
        ),
    ), sort_keys=True).encode('utf-8')
])
def test_inventory_file_fail(mocker, error_result):
    open_url = OpenUrlProxy([
        OpenUrlCall('GET', 200)
        .result_error(error_result)
        .expect_url('{0}/server'.format(BASE_URL)),
    ])
    mocker.patch('ansible_collections.community.hrobot.plugins.module_utils.robot.open_url', open_url)
    mocker.patch('ansible.inventory.manager.unfrackpath', mock_unfrackpath_noop)
    mocker.patch('os.path.exists', lambda x: True)
    mocker.patch('os.access', lambda x, y: True)

    inventory_filename = "test.robot.yml"
    C.INVENTORY_ENABLED = ['community.hrobot.robot']
    inventory_file = {inventory_filename: textwrap.dedent("""\
    ---
    plugin: community.hrobot.robot
    hetzner_user: test
    hetzner_password: hunter2
    filters:
      dc: foo
    """)}
    im = InventoryManager(loader=DictDataLoader(inventory_file), sources=inventory_filename)
    open_url.assert_is_done()

    assert not im._inventory.hosts
    assert '1.2.3.4' not in im._inventory.hosts
    assert 'test-server' not in im._inventory.hosts
    assert 'test-server-2' not in im._inventory.hosts
    assert len(im._inventory.groups['ungrouped'].hosts) == 0
    assert len(im._inventory.groups['all'].hosts) == 0


def test_inventory_wrong_file(mocker):
    open_url = OpenUrlProxy([])
    mocker.patch('ansible_collections.community.hrobot.plugins.module_utils.robot.open_url', open_url)
    mocker.patch('ansible.inventory.manager.unfrackpath', mock_unfrackpath_noop)
    mocker.patch('os.path.exists', lambda x: True)
    mocker.patch('os.access', lambda x, y: True)

    inventory_filename = "test.bobot.yml"
    C.INVENTORY_ENABLED = ['community.hrobot.robot']
    inventory_file = {inventory_filename: textwrap.dedent("""\
    ---
    plugin: community.hrobot.robot
    hetzner_user: test
    hetzner_password: hunter2
    """)}
    im = InventoryManager(loader=DictDataLoader(inventory_file), sources=inventory_filename)
    open_url.assert_is_done()

    assert not im._inventory.hosts
    assert '1.2.3.4' not in im._inventory.hosts
    assert 'test-server' not in im._inventory.hosts
    assert 'test-server-2' not in im._inventory.hosts
    assert len(im._inventory.groups['ungrouped'].hosts) == 0
    assert len(im._inventory.groups['all'].hosts) == 0


def test_inventory_file_collision(mocker):
    open_url = OpenUrlProxy([
        OpenUrlCall('GET', 200)
        .result_json([
            {
                'server': {
                    'server_ip': '1.2.3.4',
                    'server_name': 'test-server',
                },
            },
            {
                'server': {
                    'server_ip': '1.2.3.5',
                    'server_name': 'test-server',
                },
            },
        ])
        .expect_url('{0}/server'.format(BASE_URL)),
    ])
    mocker.patch('ansible_collections.community.hrobot.plugins.module_utils.robot.open_url', open_url)
    mocker.patch('ansible.inventory.manager.unfrackpath', mock_unfrackpath_noop)
    mocker.patch('os.path.exists', lambda x: True)
    mocker.patch('os.access', lambda x, y: True)

    inventory_filename = "test.robot.yaml"
    C.INVENTORY_ENABLED = ['community.hrobot.robot']
    inventory_file = {inventory_filename: textwrap.dedent("""\
    ---
    plugin: community.hrobot.robot
    hetzner_user: test
    hetzner_password: hunter2
    """)}
    im = InventoryManager(loader=DictDataLoader(inventory_file), sources=inventory_filename)
    open_url.assert_is_done()

    assert im._inventory.hosts
    assert 'test-server' in im._inventory.hosts
    assert im._inventory.get_host('test-server').get_vars()['ansible_host'] == '1.2.3.4'
    assert im._inventory.get_host('test-server') in im._inventory.groups['ungrouped'].hosts
    assert len(im._inventory.groups['ungrouped'].hosts) == 1
    assert len(im._inventory.groups['all'].hosts) == 0
    # TODO: check for warning
