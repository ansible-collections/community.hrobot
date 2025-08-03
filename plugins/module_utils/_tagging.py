# -*- coding: utf-8 -*-

# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# This code is licensed under the following two licenses:
# - Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# - GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import absolute_import, division, print_function
__metaclass__ = type


try:
    from ansible.module_utils.datatag import deprecate_value as _deprecate_value
    HAS_DEPRECATE_VALUE = True
except ImportError:
    HAS_DEPRECATE_VALUE = False


def deprecate_value(value, msg, version, help_text=None):
    """
    Given a value, tag it as deprecated (with message, removal version, and optional help text).

    For ansible-core versions that do not support data tagging, simply returns the value as-is.
    """
    if not HAS_DEPRECATE_VALUE:
        return value
    return _deprecate_value(
        value,
        msg,
        collection_name="community.hrobot",
        version=version,
        help_text=help_text,
    )
