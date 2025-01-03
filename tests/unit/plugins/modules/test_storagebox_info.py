# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import storagebox_info


STORAGEBOX_MINIMUM_DATA = [
    {
        'storagebox': {
            'id': 123456,
            'login': 'u12345',
            'name': 'Backup Server 1',
            'product': 'BX60',
            'cancelled': False,
            'locked': False,
            'location': 'FSN1',
            'linked_server': 1234567,
            'paid_until': '2015-10-23',
        },
    },
    {
        'storagebox': {
            'id': 23,
            'login': 'u23',
            'name': 'Backup Server 2',
            'product': 'BX11',
            'cancelled': True,
            'locked': False,
            'location': 'HEL1',
            'linked_server': None,
            'paid_until': '2025-01-31',
        },
    },
]


STORAGEBOX_DETAIL_DATA = {
    23: {
        'storagebox': {
            'id': 23,
            'login': 'u23',
            'name': 'Backup Server 2',
            'product': 'BX11',
            'cancelled': True,
            'locked': False,
            'location': 'HEL1',
            'linked_server': None,
            'paid_until': '2025-01-31',
            'disk_quota': 1234,
            'disk_usage': 123,
            'disk_usage_data': 50,
            'disk_usage_snapshots': 73,
            'webdav': False,
            'samba': False,
            'ssh': True,
            'external_reachability': True,
            'zfs': False,
            'server': 'u23.your-storagebox.de',
            'host_system': 'HEL1-FOOBAR'
        },
    },
    123456: {
        'storagebox': {
            'id': 123456,
            'login': 'u12345',
            'name': 'Backup Server 1',
            'product': 'BX60',
            'cancelled': False,
            'locked': False,
            'location': 'FSN1',
            'linked_server': 1234567,
            'paid_until': '2015-10-23',
            'disk_quota': 10240000,
            'disk_usage': 900,
            'disk_usage_data': 500,
            'disk_usage_snapshots': 400,
            'webdav': True,
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'zfs': False,
            'server': 'u12345.your-storagebox.de',
            'host_system': 'FSN1-BX355'
        },
    },
}


class TestHetznerStorageboxInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_storagebox_id(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 1
        assert result['storageboxes'][0] == STORAGEBOX_DETAIL_DATA[23]['storagebox']

    def test_server_number_unknown(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/storagebox/1'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_MINIMUM_DATA)
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == STORAGEBOX_MINIMUM_DATA[0]['storagebox']
        assert result['storageboxes'][1] == STORAGEBOX_MINIMUM_DATA[1]['storagebox']

    def test_linked_server_number(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'linked_server_number': 1234567,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_MINIMUM_DATA[0])
            .expect_form_value('linked_server', '1234567')
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 1
        assert result['storageboxes'][0] == STORAGEBOX_MINIMUM_DATA[0]['storagebox']

    def test_linked_server_number_unknown(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'linked_server_number': 1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_form_value('linked_server', '1')
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all_full_info(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'full_info': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_MINIMUM_DATA)
            .expect_url('{0}/storagebox'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_DETAIL_DATA[123456])
            .expect_url('{0}/storagebox/123456'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == STORAGEBOX_DETAIL_DATA[123456]['storagebox']
        assert result['storageboxes'][1] == STORAGEBOX_DETAIL_DATA[23]['storagebox']

    def test_all_none(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json([])
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all_none_error(self, mocker):
        # According to the API docs, when no storagebox is found this API can return 404.
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0
