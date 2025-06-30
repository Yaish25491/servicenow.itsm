# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


PAYLOAD_FIELDS_MAPPING = dict(
    priority=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
    urgency=[("1", "1"), ("2", "2"), ("3", "3")],
    impact=[("1", "1"), ("2", "2"), ("3", "3")],
    state=[
        ("pending", "pending"),
        ("open", "open"),
        ("work_in_progress", "work_in_progress"),
        ("closed_complete", "closed_complete"),
        ("closed_incomplete", "closed_incomplete"),
        ("closed_skipped", "closed_skipped"),
        ("closed_cancelled", "closed_cancelled"),
    ],
    approval=[
        ("requested", "requested"),
        ("approved", "approved"),
        ("rejected", "rejected"),
        ("not_requested", "not_requested"),
    ],
)