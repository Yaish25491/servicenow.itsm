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
    request_state=[
        ("draft", "draft"),
        ("submitted", "submitted"),
        ("in_process", "in_process"),
        ("delivered", "delivered"),
        ("cancelled", "cancelled"),
        ("closed_incomplete", "closed_incomplete"),
        ("closed_complete", "closed_complete"),
        ("closed_cancelled", "closed_cancelled"),
    ],
    stage=[
        ("request_approved", "request_approved"),
        ("fulfillment", "fulfillment"),
        ("delivery", "delivery"),
        ("completed", "completed"),
    ],
    approval=[
        ("requested", "requested"),
        ("approved", "approved"),
        ("rejected", "rejected"),
        ("not_requested", "not_requested"),
    ],
)