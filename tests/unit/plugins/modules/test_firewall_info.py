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
from ansible_collections.community.hrobot.plugins.modules import firewall_info


class TestHetznerFirewallInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.firewall_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    # Tests for state (absent and present)

    def test_absent(self, mocker):
        result = self.run_module_success(mocker, firewall_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 1,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json({
                'firewall': {
                    'filter_ipv6': False,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'disabled',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/1'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['firewall']['filter_ipv6'] is False
        assert result['firewall']['allowlist_hos'] is False
        assert result['firewall']['status'] == 'disabled'
        assert result['firewall']['server_ip'] == '1.2.3.4'
        assert result['firewall']['server_number'] == 1

    def test_absent_no_rules(self, mocker):
        result = self.run_module_success(mocker, firewall_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_ip': '1.2.3.4',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': False,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'disabled',
                    'whitelist_hos': False,
                    'port': 'main',
                },
            })
            .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['firewall']['filter_ipv6'] is False
        assert result['firewall']['status'] == 'disabled'
        assert result['firewall']['server_ip'] == '1.2.3.4'
        assert result['firewall']['server_number'] == 1
        assert 'rules' in result['firewall']
        assert 'input' in result['firewall']['rules']
        assert len(result['firewall']['rules']['input']) == 0

    def test_present(self, mocker):
        result = self.run_module_success(mocker, firewall_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_ip': '1.2.3.4',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'active',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['firewall']['filter_ipv6'] is True
        assert result['firewall']['status'] == 'active'
        assert result['firewall']['server_ip'] == '1.2.3.4'
        assert result['firewall']['server_number'] == 1
        assert len(result['firewall']['rules']['input']) == 0
        assert len(result['firewall']['rules']['output']) == 0

    def test_present_w_rules(self, mocker):
        result = self.run_module_success(mocker, firewall_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_ip': '1.2.3.4',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'active',
                    'whitelist_hos': True,
                    'port': 'main',
                    'rules': {
                        'input': [
                            {
                                'name': 'Accept HTTPS traffic',
                                'ip_version': 'ipv4',
                                'dst_ip': None,
                                'dst_port': '443',
                                'src_ip': None,
                                'src_port': None,
                                'protocol': 'tcp',
                                'tcp_flags': None,
                                'action': 'accept',
                            },
                            {
                                'name': None,
                                'ip_version': 'ipv4',
                                'dst_ip': None,
                                'dst_port': None,
                                'src_ip': None,
                                'src_port': None,
                                'protocol': None,
                                'tcp_flags': None,
                                'action': 'discard',
                            }
                        ],
                        'output': [
                            {
                                'name': None,
                                'ip_version': None,
                                'dst_ip': None,
                                'dst_port': None,
                                'src_ip': None,
                                'src_port': None,
                                'protocol': None,
                                'tcp_flags': None,
                                'action': 'accept',
                            }
                        ],
                    },
                },
            })
            .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['firewall']['filter_ipv6'] is True
        assert result['firewall']['allowlist_hos'] is True
        assert result['firewall']['status'] == 'active'
        assert result['firewall']['server_ip'] == '1.2.3.4'
        assert result['firewall']['server_number'] == 1
        assert len(result['firewall']['rules']['input']) == 2
        assert result['firewall']['rules']['input'][0]['name'] == 'Accept HTTPS traffic'
        assert result['firewall']['rules']['input'][0]['dst_port'] == '443'
        assert result['firewall']['rules']['input'][0]['action'] == 'accept'
        assert result['firewall']['rules']['input'][1]['dst_port'] is None
        assert result['firewall']['rules']['input'][1]['action'] == 'discard'
        assert len(result['firewall']['rules']['output']) == 1
        assert result['firewall']['rules']['output'][0]['name'] is None
        assert result['firewall']['rules']['output'][0]['ip_version'] is None
        assert result['firewall']['rules']['output'][0]['action'] == 'accept'

    # Tests for wait_for_configured in getting status

    def test_wait_get(self, mocker):
        mocker.patch('time.sleep', lambda duration: None)
        result = self.run_module_success(mocker, firewall_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 123,
            'wait_for_configured': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 123,
                    'status': 'in process',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/123'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 123,
                    'status': 'in process',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/123'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': False,
                    'server_ip': '1.2.3.4',
                    'server_number': 123,
                    'status': 'active',
                    'whitelist_hos': True,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/123'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['firewall']['filter_ipv6'] is False
        assert result['firewall']['whitelist_hos'] is True
        assert result['firewall']['allowlist_hos'] is True
        assert result['firewall']['status'] == 'active'
        assert result['firewall']['server_ip'] == '1.2.3.4'
        assert result['firewall']['server_number'] == 123

    def test_wait_get_timeout(self, mocker):
        mocker.patch('time.sleep', lambda duration: None)
        result = self.run_module_failed(mocker, firewall_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_ip': '1.2.3.4',
            'wait_for_configured': True,
            'timeout': 0,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'in process',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'in process',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['msg'] == 'Timeout while waiting for firewall to be configured.'

    def test_nowait_get(self, mocker):
        result = self.run_module_success(mocker, firewall_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_ip': '1.2.3.4',
            'wait_for_configured': False,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'firewall': {
                    'filter_ipv6': True,
                    'server_ip': '1.2.3.4',
                    'server_number': 1,
                    'status': 'in process',
                    'whitelist_hos': False,
                    'port': 'main',
                    'rules': {
                        'input': [],
                        'output': [],
                    },
                },
            })
            .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['firewall']['status'] == 'in process'
        assert result['firewall']['server_ip'] == '1.2.3.4'
        assert result['firewall']['server_number'] == 1
