# Copyright (c) 2025 Victor LEFEBVRE <dev@vic1707.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import (
    storagebox_subaccount,
)

STORAGEBOX_SUBACCOUNTS = [
    {
        "subaccount": {
            "username": "u2342-sub1",
            "accountid": "u2342",
            "server": "u12345-sub1.your-storagebox.de",
            "homedirectory": "test",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": False,
            "readonly": False,
            "createtime": "2017-05-24 00:00:00",
            "comment": "Test account",
        }
    },
    {
        "subaccount": {
            "username": "u2342-sub2",
            "accountid": "u2342",
            "server": "u12345-sub2.your-storagebox.de",
            "homedirectory": "test2",
            "samba": False,
            "ssh": True,
            "external_reachability": True,
            "webdav": True,
            "readonly": False,
            "createtime": "2025-01-24 00:00:00",
            "comment": "Test account 2",
        }
    },
]


class TestHetznerStorageboxSubbacount(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_subaccount.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'subaccount': {}
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storage Box with ID 23 does not exist',
                }
            })
            .expect_url(BASE_URL + '/storagebox/23/subaccount')
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'

    def test_delete_unknown_subaccount_noop(self, mocker):
        """Test deletion of a subaccount that doesn't exist (no-op)."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'subaccount': {
                'state': 'absent',
                'username': 'ghost_user',
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/1234/subaccount')
        ])

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['created_subaccount'] is None

    def test_delete_existing_subaccount(self, mocker):
        """Test successful deletion of an existing subaccount."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'subaccount': {
                'state': 'absent',
                'username': 'u2342-sub2',
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

            FetchUrlCall('DELETE', 200)
            .result_json({})
            .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub2')
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['created_subaccount'] is None

    def test_create_subaccount(self, mocker):
        new_subaccount = {
            'homedirectory': '/data/newsub',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount'
        }

        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'subaccount': new_subaccount
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value('homedirectory', '/data/newsub')
                .expect_form_value('samba', 'true')
                .expect_form_value('ssh', 'false')
                .expect_form_value('webdav', 'true')
                .expect_form_value('readonly', 'false')
                .expect_form_value('comment', 'My new subaccount')
                .result_json({
                    'username': 'generated_user',
                    'homedirectory': '/data/newsub',
                    'password': 'autogeneratedpass123'
                }),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['created_subaccount'] == {
            'username': 'generated_user',
            'homedirectory': '/data/newsub',
            'password': 'autogeneratedpass123'
        }

    def test_update_subaccount_noop(self, mocker):
        import copy
        updated_sub = copy.deepcopy(STORAGEBOX_SUBACCOUNTS[0]['subaccount'])
        del updated_sub['accountid'], updated_sub['createtime'], updated_sub['server']

        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'subaccount': updated_sub
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),
            ]
        )

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['created_subaccount'] is None

    def test_update_subaccount_changed(self, mocker):
        import copy
        updated_sub = copy.deepcopy(STORAGEBOX_SUBACCOUNTS[0]['subaccount'])
        del updated_sub['accountid'], updated_sub['createtime'], updated_sub['server']
        updated_sub['comment'] = 'new comment'

        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'subaccount': updated_sub
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('PUT', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/' + updated_sub['username'])
                .expect_form_value("homedirectory", updated_sub["homedirectory"])
                .expect_form_value("samba", str(updated_sub["samba"]).lower())
                .expect_form_value("ssh", str(updated_sub["ssh"]).lower())
                .expect_form_value("external_reachability", str(updated_sub["external_reachability"]).lower())
                .expect_form_value("webdav", str(updated_sub["webdav"]).lower())
                .expect_form_value("readonly", str(updated_sub["readonly"]).lower())
                .expect_form_value("comment", updated_sub["comment"])
                .result_json({})
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['created_subaccount'] is None

    def test_update_password_only(self, mocker):
        import copy
        updated_sub = copy.deepcopy(STORAGEBOX_SUBACCOUNTS[0]['subaccount'])
        del updated_sub['accountid'], updated_sub['createtime'], updated_sub['server']
        updated_sub['password'] = 'newsecurepassword'

        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'subaccount': updated_sub
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub1/password')
                .expect_form_value("password", "newsecurepassword")
                .result_json({})
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is True
        assert result['created_subaccount'] is None

    def test_update_subaccount_invalid_password(self, mocker):
        updated_sub = STORAGEBOX_SUBACCOUNTS[0]['subaccount']
        del updated_sub['accountid'], updated_sub['createtime'], updated_sub['server']
        updated_sub['password'] = '123'

        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'subaccount': updated_sub
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 400)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub1/password')
                .expect_form_value("password", "123")
                .result_json({
                    "error": {
                        "status": 400,
                        "code": "INVALID_PASSWORD",
                        "message": "Password does not meet security requirements"
                    }
                })
            ]
        )

        assert result['msg'] == "Request failed: 400 INVALID_PASSWORD (Password does not meet security requirements)"

    def test_create_subaccount_invalid_password(self, mocker):
        new_sub = {
            'homedirectory': '/data/newsub',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'Invalid password attempt',
            'password': '123'
        }

        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'subaccount': new_sub
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 400)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value("password", "123")
                .result_json({
                    "error": {
                        "status": 400,
                        "code": "INVALID_PASSWORD",
                        "message": "Password does not meet security requirements"
                    }
                })
            ]
        )

        assert result['msg'] == "Request failed: 400 INVALID_PASSWORD (Password does not meet security requirements)"
