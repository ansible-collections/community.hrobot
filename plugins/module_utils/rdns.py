# -*- coding: utf-8 -*-

# Copyright (c), name <email>, year
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import json

from ansible.module_utils.six.moves.urllib.parse import urlencode

from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    BASE_URL,
    fetch_url_json,
)


def get_rdns(module, ip):
    '''
    Get reverse DNS record of IP.

    See https://robot.your-server.de/doc/webservice/en.html#get-rdns-ip
    '''
    url = "{0}/rdns/{1}".format(BASE_URL, ip)
    result, error = fetch_url_json(module, url)
    if 'rdns' not in result:
        module.fail_json(msg='Cannot interpret result: {0}'.format(json.dumps(result, sort_keys=True)))
    return result['rdns']['ptr']


def set_rdns(module, ip, ptr, timeout=180):
    '''
    Set reverse DNS of IP.

    See https://robot.your-server.de/doc/webservice/en.html#post-rdns-ip
    '''
    url = "{0}/rdns/{1}".format(BASE_URL, ip)
    if ptr is None:
        result, error = fetch_url_json(
            module,
            url,
            method='DELETE',
            timeout=timeout
        )
    else:
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = dict(
            ptr=ptr,
        )
        result, error = fetch_url_json(
            module,
            url,
            method='POST',
            timeout=timeout,
            data=urlencode(data),
            headers=headers
        )
    if result is 'ok':
        return True
    elif error is not None:
        return ptr, False
    else:
        return result['rdns']['ptr'], True
