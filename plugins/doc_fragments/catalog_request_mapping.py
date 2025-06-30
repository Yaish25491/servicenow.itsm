# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  catalog_request_mapping:
    version_added: "2.7.0"
    description:
      - User mapping for I(Catalog request) object, where user can override Choice Lists values for objects.
    type: dict
    suboptions:
      priority:
        description:
          - Priority of the catalog request.
          - Priority 1 is the highest, 5 is the lowest priority.
        type: dict
      urgency:
        description:
          - Urgency of the catalog request.
          - Urgency 1 is the highest, 3 is the lowest urgency.
        type: dict
      impact:
        description:
          - Impact of the catalog request.
          - Impact 1 is the highest, 3 is the lowest impact.
        type: dict
      request_state:
        description:
          - The current state of the catalog request.
          - Special value that can not be overridden is C(present) and C(absent), which would create/update or remove a catalog request from ServiceNow.
        type: dict
      stage:
        description:
          - Current stage of the catalog request workflow.
        type: dict
      approval:
        description:
          - Approval status of the catalog request.
        type: dict
"""