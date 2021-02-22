# -*- coding: utf-8 -*-

# Copyright (c), Felix Fontein <felix@fontein.de>, 2019
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible.module_utils.urls import fetch_url, open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError

import json
import time


ROBOT_DEFAULT_ARGUMENT_SPEC = dict(
    hetzner_user=dict(type='str', required=True),
    hetzner_password=dict(type='str', required=True, no_log=True),
)

# The API endpoint is fixed.
BASE_URL = "https://robot-ws.your-server.de"


class PluginException(Exception):
    def __init__(self, message):
        super(PluginException, self).__init__(message)
        self.error_message = message


def plugin_open_url_json(plugin, url, method='GET', timeout=10, data=None, headers=None, accept_errors=None):
    '''
    Make general request to Hetzner's JSON robot API.
    '''
    user = plugin.get_option('hetzner_user')
    password = plugin.get_option('hetzner_password')
    try:
        response = open_url(
            url,
            url_username=user,
            url_password=password,
            force_basic_auth=True,
            data=data,
            headers=headers,
            method=method,
            timeout=timeout,
        )
        content = response.read()
    except HTTPError as e:
        try:
            content = e.read()
        except AttributeError:
            content = b''
    except Exception as e:
        raise PluginException('Failed request to Hetzner Robot server endpoint {0}: {1}'.format(url, e))

    if not content:
        raise PluginException('Cannot retrieve content from {0}'.format(url))

    try:
        result = json.loads(content.decode('utf-8'))
        if 'error' in result:
            if accept_errors:
                if result['error']['code'] in accept_errors:
                    return result, result['error']['code']
            raise PluginException('Request failed: {0} {1} ({2})'.format(
                result['error']['status'],
                result['error']['code'],
                result['error']['message']
            ))
        return result, None
    except ValueError:
        raise PluginException('Cannot decode content retrieved from {0}'.format(url))


def fetch_url_json(module, url, method='GET', timeout=10, data=None, headers=None, accept_errors=None):
    '''
    Make general request to Hetzner's JSON robot API.
    '''
    module.params['url_username'] = module.params['hetzner_user']
    module.params['url_password'] = module.params['hetzner_password']
    module.params['force_basic_auth'] = True
    resp, info = fetch_url(module, url, method=method, timeout=timeout, data=data, headers=headers)
    status_code = info["status"]
    try:
        content = resp.read()
    except AttributeError:
        content = info.pop('body', None)

    if not content and status_code != 200:
        module.fail_json(msg='Cannot retrieve content from {0}'.format(url))

    if content:
        try:
            print("lol=")
            result = module.from_json(content.decode('utf8'))
            if 'error' in result:
                if accept_errors:
                    if result['error']['code'] in accept_errors:
                        return result, result['error']['code']
                module.fail_json(msg='Request failed: {0} {1} ({2})'.format(
                    result['error']['status'],
                    result['error']['code'],
                    result['error']['message']
                ))
            return result, None
        except ValueError:
            module.fail_json(msg='Cannot decode content retrieved from {0}'.format(url))
    else:
        # status code 200 and empty content
        result = 'ok'
        return result, None


class CheckDoneTimeoutException(Exception):
    def __init__(self, result, error):
        super(CheckDoneTimeoutException, self).__init__()
        self.result = result
        self.error = error


def fetch_url_json_with_retries(module, url, check_done_callback, check_done_delay=10, check_done_timeout=180, skip_first=False, **kwargs):
    '''
    Make general request to Hetzner's JSON robot API, with retries until a condition is satisfied.

    The condition is tested by calling ``check_done_callback(result, error)``. If it is not satisfied,
    it will be retried with delays ``check_done_delay`` (in seconds) until a total timeout of
    ``check_done_timeout`` (in seconds) since the time the first request is started is reached.

    If ``skip_first`` is specified, will assume that a first call has already been made and will
    directly start with waiting.
    '''
    start_time = time.time()
    if not skip_first:
        result, error = fetch_url_json(module, url, **kwargs)
        if check_done_callback(result, error):
            return result, error
    while True:
        elapsed = (time.time() - start_time)
        left_time = check_done_timeout - elapsed
        time.sleep(max(min(check_done_delay, left_time), 0))
        result, error = fetch_url_json(module, url, **kwargs)
        if check_done_callback(result, error):
            return result, error
        if left_time < check_done_delay:
            raise CheckDoneTimeoutException(result, error)
