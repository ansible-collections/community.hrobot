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
from ansible_collections.community.hrobot.plugins.modules import storagebox


STORAGEBOX_KEYS = ('name', 'webdav', 'samba', 'ssh', 'external_reachability', 'zfs')

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


def update_info(id, **updates):
    result = {
        'storagebox': dict(STORAGEBOX_DETAIL_DATA[id]['storagebox']),
    }
    result['storagebox'].update(updates)
    return result


class TestHetznerStorageboxInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_idempotent(self, mocker):
        updated = update_info(23)
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup Server 2',
            'webdav': False,
            'samba': False,
            'ssh': True,
            'external_reachability': True,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        for key in STORAGEBOX_KEYS:
            assert result[key] == updated['storagebox'][key], "Unexpected difference for {0!r}".format(key)

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_user': '',
            'hetzner_password': '',
            'id': 1,
        }, [
            FetchUrlCall('GET', 404)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storagebox not found',
                },
            })
            .expect_url('{0}/storagebox/1'.format(BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 1 does not exist'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_user': '',
            'hetzner_password': '',
            'id': 23,
            'name': 'Backup',
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 400)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 400,
                    'code': 'INVALID_INPUT',
                    'message': 'Invalid input',
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The values to update were invalid ({"storagebox_name": "Backup"})'

    def test_change_name(self, mocker):
        updated = update_info(23, name='Backup')
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json(updated)
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        for key in STORAGEBOX_KEYS:
            assert result[key] == updated['storagebox'][key], "Unexpected difference for {0!r}".format(key)
