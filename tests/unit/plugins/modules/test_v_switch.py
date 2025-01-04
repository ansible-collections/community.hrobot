# Copyright (c) 2019 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from datetime import datetime

from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import v_switch


# pylint: disable=dangerous-default-value
# we are not mutating this value
def create_v_switch_data(vlan, name, server=[]):
    return {
        'id': 4321,
        'name': name,
        'vlan': vlan,
        'cancelled': False,
        'server': server,
        'subnet': [],
        'cloud_network': [],
    }


def create_v_switches_data(vlan, name, id_=4321):
    return [
        {
            'id': id_,
            'name': name,
            'vlan': vlan,
            'cancelled': False,
        }
    ]


def create_server_data(ip, id_, status='ready'):
    return {
        'server_ip': ip,
        'server_ipv6_net': '2a01:4f8:111:4221::',
        'server_number': id_,
        'status': status,
    }


class TestHetznerVSwitch(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = (
        'ansible_collections.community.hrobot.plugins.modules.v_switch.AnsibleModule'
    )
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = (
        'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'
    )

    def test_idempotent(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )
        assert result['changed'] is False
        assert result['v_switch'] == create_v_switch_data(4010, 'foo')

    def test_not_found_after_list(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 404)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json({
                    'error': {
                        'status': 404,
                        'code': 'NOT_FOUND',
                        'message': 'Cannot find vswitch',
                    },
                })
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == 'vSwitch not found.'

    def test_not_unique(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo') + create_v_switches_data(4010, 'foo', id_=1234))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == 'Multiple vSwitches with same name and VLAN ID in non cancelled status. Clean it.'

    def test_create(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json([])
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('POST', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['changed'] is True
        assert result['v_switch'] == create_v_switch_data(4010, 'foo')

    def test_create_check(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json([])
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['changed'] is True
        assert 'v_switch' not in result

    def test_v_switch_different_name(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'not_matching_name',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('POST', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'not_matching_name'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['changed'] is True
        assert result['v_switch'] == create_v_switch_data(4010, 'not_matching_name')

    def test_v_switch_unauthorized_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'vlan': 4010,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 401)
                .result_json(
                    {
                        'error': {
                            'status': 401,
                            'code': 'UNAUTHORIZED',
                            'message': 'Unauthorized',
                        },
                    }
                )
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == 'Please check your current user and password configuration'

    def test_v_switch_limit_reached_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4000,
                'name': 'new vswitch',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('POST', 409)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    {
                        'error': {
                            'status': 409,
                            'code': 'VSWITCH_LIMIT_REACHED',
                            'message': 'The maximum count of vSwitches is reached',
                        },
                    }
                )
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == 'The maximum count of vSwitches is reached'

    def test_v_switch_invalid_input_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 40100,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('POST', 400)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    {
                        'error': {
                            'status': 400,
                            'code': 'INVALID_INPUT',
                            'message': 'invalid input',
                            'missing': None,
                            'invalid': ['vlan'],
                        },
                    }
                )
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == "vSwitch invalid parameter (vlan)"

    def test_delete(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'state': 'absent',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('cancellation_date', datetime.now().strftime('%y-%m-%d'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['changed'] is True

    def test_delete_check(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'state': 'absent',
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['changed'] is True

    def test_delete_idempotent(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'state': 'absent',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json([])
                .expect_url('{0}/vswitch'.format(BASE_URL)),
            ],
        )

        assert result['changed'] is False

    def test_delete_not_found(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'state': 'absent',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 404)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('cancellation_date', datetime.now().strftime('%y-%m-%d'))
                .result_json({
                    'error': {
                        'status': 404,
                        'code': 'NOT_FOUND',
                        'message': 'not found',
                    },
                })
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['msg'] == 'vSwitch not found to delete'

    def test_delete_conflict(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'state': 'absent',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 404)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('cancellation_date', datetime.now().strftime('%y-%m-%d'))
                .result_json({
                    'error': {
                        'status': 409,
                        'code': 'CONFLICT',
                        'message': 'Already cancelled',
                    },
                })
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['msg'] == 'The vSwitch is already cancelled'

    def test_delete_invalid_input(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'state': 'absent',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 404)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('cancellation_date', datetime.now().strftime('%y-%m-%d'))
                .result_json({
                    'error': {
                        'status': 400,
                        'code': 'INVALID_INPUT',
                        'message': 'Invalid input',
                        'invalid': 'foo',
                        'missing': None,
                    },
                })
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['msg'] in (
            "vSwitch invalid parameter ('foo')",
            "vSwitch invalid parameter (u'foo')",
        )

    def test_create_with_server(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json([])
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('POST', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321)],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
        )
        assert result['changed'] is True

    def test_is_all_servers_ready(self):
        result = v_switch.is_all_servers_ready(
            create_v_switch_data(
                4010,
                'foo',
                server=[],
            ),
            None,
        )
        assert result is True

        result = v_switch.is_all_servers_ready(
            create_v_switch_data(
                4010,
                'foo',
                server=[
                    create_server_data('123.123.123.123', 321),
                    create_server_data('123.123.123.124', 322),
                ],
            ),
            None,
        )
        assert result is True

        result = v_switch.is_all_servers_ready(
            create_v_switch_data(
                4010,
                'foo',
                server=[
                    create_server_data('123.123.123.123', 321, status='in process'),
                    create_server_data('123.123.123.124', 322),
                ],
            ),
            None,
        )
        assert result is False

    def test_get_servers_to_delete(self):
        current_servers = [
            create_server_data('123.123.123.123', 321),
            create_server_data('123.123.123.124', 322),
        ]
        desired_servers = ['321']
        result = v_switch.get_servers_to_delete(current_servers, desired_servers)
        assert result == ['123.123.123.124']

        current_servers = [
            create_server_data('123.123.123.123', 321),
            create_server_data('123.123.123.124', 322),
        ]
        desired_servers = []
        result = v_switch.get_servers_to_delete(current_servers, desired_servers)
        assert result == ['123.123.123.123', '123.123.123.124']

        current_servers = [
            create_server_data('123.123.123.123', 321),
            create_server_data('123.123.123.124', 322),
        ]
        desired_servers = ['123.123.123.123']
        result = v_switch.get_servers_to_delete(current_servers, desired_servers)
        assert result == ['123.123.123.124']

        current_servers = [
            create_server_data('check_default_ipv6', 321),
        ]
        desired_servers = ['2a01:4f8:111:4221::']
        result = v_switch.get_servers_to_delete(current_servers, desired_servers)
        assert result == []

        current_servers = []
        desired_servers = ['123.123.123.123']
        result = v_switch.get_servers_to_delete(current_servers, desired_servers)
        assert result == []

    def test_get_servers_to_add(self):
        current_servers = [
            create_server_data('123.123.123.123', 321),
            create_server_data('123.123.123.124', 322),
        ]
        desired_servers = ['321']
        result = v_switch.get_servers_to_add(current_servers, desired_servers)
        assert result == []

        current_servers = [
            create_server_data('123.123.123.123', 321),
            create_server_data('123.123.123.124', 322),
        ]
        desired_servers = []
        result = v_switch.get_servers_to_add(current_servers, desired_servers)
        assert result == []

        current_servers = [
            create_server_data('123.123.123.123', 321),
            create_server_data('123.123.123.124', 322),
        ]
        desired_servers = ['123.123.123.123']
        result = v_switch.get_servers_to_add(current_servers, desired_servers)
        assert result == []

        current_servers = [
            create_server_data('check_default_ipv6', 321),
        ]
        desired_servers = ['2a01:4f8:111:4221::']
        result = v_switch.get_servers_to_add(current_servers, desired_servers)
        assert result == []

        current_servers = []
        desired_servers = ['123.123.123.123']
        result = v_switch.get_servers_to_add(current_servers, desired_servers)
        assert result == ['123.123.123.123']

        current_servers = [create_server_data('123.123.123.123', 321)]
        desired_servers = ['321', '322']
        result = v_switch.get_servers_to_add(current_servers, desired_servers)
        assert result == ['322']

    def test_add_server(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321)],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
        )
        assert result['changed'] is True

    def test_add_server_check(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(4010, 'foo')
        assert result['changed'] is True

    def test_add_server_no_wait(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
                'wait': False,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321, status='in process')],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321, status='in process')]
        )
        assert result['changed'] is True

    def test_add_multiple_servers(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123', '123.123.123.124'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[0]', '123.123.123.123')
                .expect_form_value('server[1]', '123.123.123.124')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[
                            create_server_data('123.123.123.123', 321),
                            create_server_data('123.123.123.124', 322),
                        ],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(
            4010,
            'foo',
            server=[
                create_server_data('123.123.123.123', 321),
                create_server_data('123.123.123.124', 322),
            ],
        )
        assert result['changed'] is True

    def test_add_server_timeout_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
                'timeout': 0,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321, status='in process')],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321, status='in process')],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['msg'] == "Timeout waiting vSwitch operation to finish"

    def test_add_server_idempotent(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )
        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
        )
        assert result['changed'] is False

    def test_add_server_server_not_found_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json(
                    {
                        'error': {
                            'status': 404,
                            'code': 'SERVER_NOT_FOUND',
                            'message': 'server "123.123.123.123" not found',
                        },
                    }
                )
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == 'server "123.123.123.123" not found'

    def test_add_server_vlan_invalid_input(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json({
                    'error': {
                        'status': 400,
                        'code': 'INVALID_INPUT',
                        'message': 'Invalid input',
                        'invalid': ['foobar', 'bazbam'],
                        'missing': None,
                    },
                })
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == "Invalid parameter adding server (foobar, bazbam)"

    def test_add_server_vlan_not_unique_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json(
                    {
                        'error': {
                            'status': 409,
                            'code': 'VSWITCH_VLAN_NOT_UNIQUE',
                            'message': 'vlan of vswitch is already in use at server EX62-NVMe (123.123.123.123) example.com, please change vlan',
                        },
                    }
                )
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert (
            result['msg']
            == "vlan of vswitch is already in use at server EX62-NVMe (123.123.123.123) example.com, please change vlan"
        )

    def test_add_server_vswitch_in_process_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json(
                    {
                        'error': {
                            'status': 409,
                            'code': 'VSWITCH_IN_PROCESS',
                            'message': 'There is a update running, therefore the vswitch can not be updated',
                        },
                    }
                )
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert (
            result['msg'] == "There is a update running, therefore the vswitch can not be updated"
        )

    def test_add_server_server_limit_reached_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['123.123.123.123'],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switch_data(4010, 'foo'))
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('POST', 201)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json(
                    {
                        'error': {
                            'status': 409,
                            'code': 'VSWITCH_SERVER_LIMIT_REACHED',
                            'message': 'The maximum number of servers is reached for this vSwitch',
                        },
                    }
                )
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == "The maximum number of servers is reached for this vSwitch"

    def test_not_delete_if_servers_not_defined(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )
        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
        )
        assert result['changed'] is False

    def test_delete_server(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': [],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(4010, 'foo')
        assert result['changed'] is True

    def test_delete_server_check(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': [],
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
        )
        assert result['changed'] is True

    def test_delete_server_wait(self, mocker):
        result = self.run_module_success(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': ['321'],
                'timeout': 0,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[
                            create_server_data('123.123.123.123', 321),
                            create_server_data('123.123.123.124', 322),
                        ],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.124')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[
                            create_server_data('123.123.123.123', 321),
                            create_server_data('123.123.123.124', 322, status='in process'),
                        ],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )

        assert result['v_switch'] == create_v_switch_data(
            4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
        )
        assert result['changed'] is True

    def test_delete_server_timeout_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': [],
                'timeout': 0,
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321, status='in process')],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010,
                        'foo',
                        server=[create_server_data('123.123.123.123', 321, status='in process')],
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == "Timeout waiting vSwitch operation to finish"

    def test_delete_server_server_not_found(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': [],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json(
                    {
                        'error': {
                            'status': 404,
                            'code': 'SERVER_NOT_FOUND',
                            'message': 'server "123.123.123.123" not found',
                        },
                    }
                )
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert result['msg'] == 'server "123.123.123.123" not found'

    def test_delete_server_in_process_error(self, mocker):
        result = self.run_module_failed(
            mocker,
            v_switch,
            {
                'hetzner_user': 'test',
                'hetzner_password': 'hunter2',
                'vlan': 4010,
                'name': 'foo',
                'servers': [],
            },
            [
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(create_v_switches_data(4010, 'foo'))
                .expect_url('{0}/vswitch'.format(BASE_URL)),
                FetchUrlCall('GET', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .result_json(
                    create_v_switch_data(
                        4010, 'foo', server=[create_server_data('123.123.123.123', 321)]
                    )
                )
                .expect_url('{0}/vswitch/4321'.format(BASE_URL)),
                FetchUrlCall('DELETE', 200)
                .expect_basic_auth('test', 'hunter2')
                .expect_force_basic_auth(True)
                .expect_form_value('server[]', '123.123.123.123')
                .result_json(
                    {
                        'error': {
                            'status': 409,
                            'code': 'VSWITCH_IN_PROCESS',
                            'message': 'There is a update running, therefore the vswitch can not be updated',
                        },
                    }
                )
                .expect_url('{0}/vswitch/4321/server'.format(BASE_URL)),
            ],
        )
        assert (
            result['msg'] == "There is a update running, therefore the vswitch can not be updated"
        )
