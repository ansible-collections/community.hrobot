# Copyright (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import ssh_key_info


class TestHetznerSSHKeyInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.ssh_key_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_no_keys(self, mocker):
        result = self.run_module_success(mocker, ssh_key_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
        }, [
            FetchUrlCall('GET', 200)
            .result_json([])
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_url('{0}/key'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['ssh_keys'] == []

    def test_no_keys_404(self, mocker):
        result = self.run_module_success(mocker, ssh_key_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'No keys found',
                },
            })
            .expect_url('{0}/key'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['ssh_keys'] == []

    def test_single_key(self, mocker):
        result = self.run_module_success(mocker, ssh_key_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json([
                {
                    'key': {
                        'name': 'key1',
                        'fingerprint': '56:29:99:a4:5d:ed:ac:95:c1:f5:88:82:90:5d:dd:10',
                        'type': 'ECDSA',
                        'size': 521,
                        'data': 'ecdsa-sha2-nistp521 AAAAE2VjZHNh ...'
                    },
                },
            ])
            .expect_url('{0}/key'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['ssh_keys'] == [{
            'name': 'key1',
            'fingerprint': '56:29:99:a4:5d:ed:ac:95:c1:f5:88:82:90:5d:dd:10',
            'type': 'ECDSA',
            'size': 521,
            'data': 'ecdsa-sha2-nistp521 AAAAE2VjZHNh ...'
        }]
