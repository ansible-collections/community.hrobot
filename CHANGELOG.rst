================================================
Community Hetzner Robot Collection Release Notes
================================================

.. contents:: Topics


v1.2.1
======

Release Summary
---------------

Maintenance release.

Minor Changes
-------------

- Generic module HTTP support code - fix usage of ``fetch_url`` with changes in latest ansible-core ``devel`` branch (https://github.com/ansible-collections/community.hrobot/pull/30).

v1.2.0
======

Release Summary
---------------

Feature release with multiple new modules.

Minor Changes
-------------

- Avoid internal ansible-core module_utils in favor of equivalent public API available since at least Ansible 2.9 (https://github.com/ansible-collections/community.hrobot/pull/18).
- firewall - rename option ``whitelist_hos`` to ``allowlist_hos``, keep old name as alias (https://github.com/ansible-collections/community.hrobot/pull/15).
- firewall, firewall_info - add return value ``allowlist_hos``, which contains the same value as ``whitelist_hos``. The old name ``whitelist_hos`` will be removed eventually (https://github.com/ansible-collections/community.hrobot/pull/15).
- robot module utils - add ``allow_empty_result`` parameter to ``plugin_open_url_json`` and ``fetch_url_json`` (https://github.com/ansible-collections/community.hrobot/pull/16).

New Modules
-----------

- community.hrobot.boot - Set boot configuration
- community.hrobot.reset - Reset a dedicated server
- community.hrobot.reverse_dns - Set or remove reverse DNS entry for IP
- community.hrobot.server - Update server information
- community.hrobot.server_info - Query information on one or more servers
- community.hrobot.ssh_key - Add, remove or update SSH key
- community.hrobot.ssh_key_info - Query information on SSH keys

v1.1.1
======

Release Summary
---------------

Bugfix release which reduces the number of HTTPS queries for the modules and plugins.

Bugfixes
--------

- robot - force HTTP basic authentication to reduce number of HTTPS requests (https://github.com/ansible-collections/community.hrobot/pull/9).

v1.1.0
======

Release Summary
---------------

Release with a new inventory plugin.

New Plugins
-----------

Inventory
~~~~~~~~~

- community.hrobot.robot - Hetzner Robot inventory source

v1.0.0
======

Release Summary
---------------

The ``community.hrobot`` continues the work on the Hetzner Robot modules from their state in ``community.general`` 1.2.0. The changes listed here are thus relative to the modules ``community.general.hetzner_*``.


Breaking Changes / Porting Guide
--------------------------------

- firewall - now requires the `ipaddress <https://pypi.org/project/ipaddress/>`_ library (https://github.com/ansible-collections/community.hrobot/pull/2).
