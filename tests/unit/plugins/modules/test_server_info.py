# Copyright (c) 2019 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import server_info


SERVER_MINIMUM_DATA = [
    {
        'server': {
            'cancelled': False,
            'dc': 'NBG1-DC1',
            'ip': [
                '1.2.3.4',
            ],
            'linked_storagebox': None,
            'paid_until': '2021-12-31',
            'product': 'EX41',
            'server_ip': '1.2.3.4',
            'server_ipv6_net': '2a01:1:2:3::',
            'server_name': 'foo',
            'server_number': 23,
            'status': 'ready',
            'subnet': [
                {
                    'ip': '2a01:1:2:3::',
                    'mask': '64',
                },
            ],
            'traffic': 'unlimited',
        },
    },
    {
        'server': {
            'cancelled': True,
            'dc': 'NBG1-DC2',
            'ip': [
                '1.2.3.5',
            ],
            'linked_storagebox': 12345,
            'paid_until': '2021-11-30',
            'product': 'EX41',
            'server_ip': '1.2.3.5',
            'server_ipv6_net': '2a01:1:5:3::',
            'server_name': 'bar',
            'server_number': 42,
            'status': 'in process',
            'subnet': [
                {
                    'ip': '2a01:1:5:3::',
                    'mask': '64',
                },
            ],
            'traffic': '1 TB',
        },
    },
]


SERVER_DETAIL_DATA = {
    23: {
        'server': {
            'cancelled': False,
            'cpanel': False,
            'dc': 'NBG1-DC1',
            'hot_swap': True,
            'ip': [
                '1.2.3.4',
            ],
            'linked_storagebox': None,
            'paid_until': '2021-12-31',
            'plesk': False,
            'product': 'EX41',
            'rescue': True,
            'reset': True,
            'server_ip': '1.2.3.4',
            'server_ipv6_net': '2a01:1:2:3::',
            'server_name': 'foo',
            'server_number': 23,
            'status': 'ready',
            'subnet': [
                {
                    'ip': '2a01:1:2:3::',
                    'mask': '64',
                },
            ],
            'traffic': 'unlimited',
            'vnc': True,
            'windows': False,
            'wol': True,
        },
    },
    42: {
        'server': {
            'cancelled': True,
            'cpanel': False,
            'dc': 'NBG1-DC2',
            'hot_swap': True,
            'ip': [
                '1.2.3.5',
            ],
            'linked_storagebox': 12345,
            'paid_until': '2021-11-30',
            'plesk': False,
            'product': 'EX41',
            'rescue': False,
            'reset': False,
            'server_ip': '1.2.3.5',
            'server_ipv6_net': '2a01:1:5:3::',
            'server_name': 'bar',
            'server_number': 42,
            'status': 'in process',
            'subnet': [
                {
                    'ip': '2a01:1:5:3::',
                    'mask': '64',
                },
            ],
            'traffic': '1 TB',
            'vnc': False,
            'windows': True,
            'wol': False,
        },
    },
}


class TestHetznerServerInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.server_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_server_number(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(SERVER_DETAIL_DATA[23])
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 1
        assert result['servers'][0] == SERVER_DETAIL_DATA[23]['server']

    def test_server_number_name_match(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'server_name': 'foo',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(SERVER_DETAIL_DATA[23])
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 1
        assert result['servers'][0] == SERVER_DETAIL_DATA[23]['server']

    def test_server_number_name_mismatch(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'server_name': 'bar',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(SERVER_DETAIL_DATA[23])
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 0

    def test_server_number_unknown(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'SERVER_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/server/1'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 0

    def test_server_all(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(SERVER_MINIMUM_DATA)
            .expect_url('{0}/server'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 2
        assert result['servers'][0] == SERVER_MINIMUM_DATA[0]['server']
        assert result['servers'][1] == SERVER_MINIMUM_DATA[1]['server']

    def test_server_name(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_name': 'foo',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(SERVER_MINIMUM_DATA)
            .expect_url('{0}/server'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 1
        assert result['servers'][0] == SERVER_MINIMUM_DATA[0]['server']

    def test_server_name_full_info(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_name': 'foo',
            'full_info': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(SERVER_MINIMUM_DATA)
            .expect_url('{0}/server'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json(SERVER_DETAIL_DATA[23])
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 1
        assert result['servers'][0] == SERVER_DETAIL_DATA[23]['server']

    def test_server_name_unknown(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_name': 'baz',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(SERVER_MINIMUM_DATA)
            .expect_url('{0}/server'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 0

    def test_server_name_none(self, mocker):
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_name': 'foo',
        }, [
            FetchUrlCall('GET', 200)
            .result_json([])
            .expect_url('{0}/server'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 0

    def test_server_name_none_error(self, mocker):
        # According to the API docs, when no server is found this API can return 404.
        # I haven't seen that in RL though...
        result = self.run_module_success(mocker, server_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_name': 'foo',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'SERVER_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/server'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['servers']) == 0
