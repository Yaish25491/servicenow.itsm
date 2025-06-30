#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: catalog_request

author:
  - ServiceNow ITSM Collection Contributors

short_description: Manage ServiceNow catalog requests

description:
  - Create, delete or update a ServiceNow catalog request (sc_request).
  - For more information, refer to the ServiceNow service catalog documentation at
    U(https://docs.servicenow.com/bundle/utah-servicenow-platform/page/product/service-catalog/concept/c_ServiceCatalogProcess.html).

version_added: 2.7.0

extends_documentation_fragment:
  - servicenow.itsm.instance
  - servicenow.itsm.sys_id
  - servicenow.itsm.number
  - servicenow.itsm.attachments
  - servicenow.itsm.catalog_request_mapping

seealso:
  - module: servicenow.itsm.catalog_request_info
  - module: servicenow.itsm.catalog_request_task
  - module: servicenow.itsm.service_catalog

options:
  state:
    description:
      - The state of the catalog request.
      - If I(state) value is C(present), the record is created or updated.
      - If I(state) value is C(absent), the record is deleted.
      - Default choices are C(present) and C(absent).
    type: str
    choices: [ present, absent ]
    default: present
  request_state:
    description:
      - The current state of the catalog request.
      - Default choices are C(draft), C(submitted), C(in_process), C(delivered), C(cancelled), C(closed_incomplete), C(closed_complete), C(closed_cancelled).
    type: str
    choices: [ draft, submitted, in_process, delivered, cancelled, closed_incomplete, closed_complete, closed_cancelled ]
  requested_for:
    description:
      - User who the catalog item is being requested for.
      - Expected value is user login name (user_name field).
    type: str
  requested_by:
    description:
      - User who requested the catalog item.
      - Expected value is user login name (user_name field).
    type: str
  assignment_group:
    description:
      - The name of the group that the catalog request is assigned to.
    type: str
  assigned_to:
    description:
      - User assigned to handle this catalog request.
      - Expected value is user login name (user_name field).
    type: str
  priority:
    description:
      - Priority of the catalog request.
      - Default choices are C(1), C(2), C(3), C(4), C(5).
      - Priority 1 is the highest, 5 is the lowest priority.
    type: str
    choices: [ "1", "2", "3", "4", "5" ]
  urgency:
    description:
      - Urgency of the catalog request.
      - Default choices are C(1), C(2), C(3).
      - Urgency 1 is the highest, 3 is the lowest urgency.
    type: str
    choices: [ "1", "2", "3" ]
  impact:
    description:
      - Impact of the catalog request.
      - Default choices are C(1), C(2), C(3).
      - Impact 1 is the highest, 3 is the lowest impact.
    type: str
    choices: [ "1", "2", "3" ]
  short_description:
    description:
      - Brief summary of the catalog request.
    type: str
  description:
    description:
      - Detailed description of the catalog request.
    type: str
  comments:
    description:
      - Additional comments for the catalog request.
    type: str
  work_notes:
    description:
      - Work notes for the catalog request (internal notes).
    type: str
  due_date:
    description:
      - Expected due date for the catalog request.
      - Expected format is YYYY-MM-DD.
    type: str
  delivery_plan:
    description:
      - Delivery plan for the catalog request.
    type: str
  delivery_task:
    description:
      - Delivery task for the catalog request.
    type: str
  stage:
    description:
      - Current stage of the catalog request.
      - Default choices are C(request_approved), C(fulfillment), C(delivery), C(completed).
    type: str
    choices: [ request_approved, fulfillment, delivery, completed ]
  approval:
    description:
      - Approval status of the catalog request.
      - Default choices are C(requested), C(approved), C(rejected), C(not_requested).
    type: str
    choices: [ requested, approved, rejected, not_requested ]
  other:
    description:
      - Optional remaining parameters.
      - For more information on optional parameters, refer to the ServiceNow
        catalog request documentation.
    type: dict
"""

EXAMPLES = r"""
- name: Create a catalog request
  servicenow.itsm.catalog_request:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass
    state: present
    requested_for: john.doe
    requested_by: jane.smith
    short_description: Request for new laptop
    description: User needs a new laptop for remote work
    priority: "2"
    urgency: "2"
    impact: "3"

- name: Update catalog request
  servicenow.itsm.catalog_request:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass
    state: present
    number: REQ0000123
    request_state: in_process
    assignment_group: IT Support
    work_notes: Started processing the request

- name: Delete catalog request
  servicenow.itsm.catalog_request:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass
    state: absent
    number: REQ0000123

- name: Create catalog request with other parameters
  servicenow.itsm.catalog_request:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass
    state: present
    requested_for: john.doe
    short_description: Custom catalog request
    other:
      special_instructions: Handle with care
      business_justification: Required for project completion
"""

RETURN = r"""
record:
  description: The catalog request record.
  returned: success
  type: dict
  sample:
    active: true
    approval: not_requested
    assigned_to: ""
    assignment_group: ""
    business_service: ""
    comments: ""
    delivery_plan: ""
    delivery_task: ""
    description: "User needs a new laptop for remote work"
    due_date: ""
    impact: "3"
    number: "REQ0000123"
    opened_at: "2024-01-15 10:30:00"
    opened_by: "jane.smith"
    priority: "2"
    request_state: "submitted"
    requested_by: "jane.smith"
    requested_for: "john.doe"
    short_description: "Request for new laptop"
    stage: "request_approved"
    state: "present"
    sys_created_by: "jane.smith"
    sys_created_on: "2024-01-15 10:30:00"
    sys_id: "b25d93a37b1200001c9c9b5b8a9619a8"
    sys_updated_by: "jane.smith"
    sys_updated_on: "2024-01-15 10:30:00"
    urgency: "2"
    work_notes: ""
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, client, errors, table, utils
from ..module_utils.utils import get_mapper
from ..module_utils.catalog_request import PAYLOAD_FIELDS_MAPPING


def ensure_absent(module, table_client):
    mapper = get_mapper(module, "catalog_request_mapping", PAYLOAD_FIELDS_MAPPING)
    query = utils.filter_dict(module.params, "sys_id", "number")
    catalog_request = table_client.get_record("sc_request", query, must_exist=False)

    if catalog_request:
        table_client.delete_record("sc_request", catalog_request, check_mode=module.check_mode)
        return True, mapper.to_ansible(catalog_request), dict(before=mapper.to_ansible(catalog_request), after=None)

    return False, None, dict(before=None, after=None)


def ensure_present(module, table_client):
    mapper = get_mapper(module, "catalog_request_mapping", PAYLOAD_FIELDS_MAPPING)
    query = utils.filter_dict(module.params, "sys_id", "number")
    payload = build_payload(module, table_client)

    if not query:
        # User did not specify existing catalog request, so we need to create a new one.
        new_catalog_request = table_client.create_record(
            "sc_request", payload, check_mode=module.check_mode
        )
        return True, mapper.to_ansible(new_catalog_request), dict(before=None, after=mapper.to_ansible(new_catalog_request))

    catalog_request = table_client.get_record("sc_request", query, must_exist=False)
    if catalog_request:
        # Update existing record
        if utils.is_superset(catalog_request, payload):
            return False, mapper.to_ansible(catalog_request), dict(before=mapper.to_ansible(catalog_request), after=mapper.to_ansible(catalog_request))

        updated_catalog_request = table_client.update_record(
            "sc_request", catalog_request, payload, check_mode=module.check_mode
        )
        return True, mapper.to_ansible(updated_catalog_request), dict(before=mapper.to_ansible(catalog_request), after=mapper.to_ansible(updated_catalog_request))
    else:
        # Create new record (this should not happen if query is not empty but record doesn't exist)
        new_catalog_request = table_client.create_record(
            "sc_request", payload, check_mode=module.check_mode
        )
        return True, mapper.to_ansible(new_catalog_request), dict(before=None, after=mapper.to_ansible(new_catalog_request))


def build_payload(module, table_client):
    payload = {}
    
    # Map simple fields
    field_mapping = {
        'request_state': 'request_state',
        'requested_for': 'requested_for',
        'requested_by': 'requested_by',
        'assignment_group': 'assignment_group',
        'assigned_to': 'assigned_to',
        'priority': 'priority',
        'urgency': 'urgency',
        'impact': 'impact',
        'short_description': 'short_description',
        'description': 'description',
        'comments': 'comments',
        'work_notes': 'work_notes',
        'due_date': 'due_date',
        'delivery_plan': 'delivery_plan',
        'delivery_task': 'delivery_task',
        'stage': 'stage',
        'approval': 'approval',
    }
    
    for ansible_field, snow_field in field_mapping.items():
        if module.params.get(ansible_field) is not None:
            payload[snow_field] = module.params[ansible_field]
    
    # Handle user lookups - only do lookups for fields that have string values (not sys_ids)
    if module.params.get('requested_for') and 'requested_for' in payload:
        # Only do lookup if the value doesn't look like a sys_id (32 char hex string)
        value = payload['requested_for']
        if not (isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value.lower())):
            payload['requested_for'] = table_client.get_record(
                'sys_user', 
                {'user_name': module.params['requested_for']},
                must_exist=True
            )['sys_id']
    
    if module.params.get('requested_by') and 'requested_by' in payload:
        value = payload['requested_by']
        if not (isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value.lower())):
            payload['requested_by'] = table_client.get_record(
                'sys_user', 
                {'user_name': module.params['requested_by']},
                must_exist=True
            )['sys_id']
    
    if module.params.get('assigned_to') and 'assigned_to' in payload:
        value = payload['assigned_to']
        if not (isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value.lower())):
            payload['assigned_to'] = table_client.get_record(
                'sys_user', 
                {'user_name': module.params['assigned_to']},
                must_exist=True
            )['sys_id']
    
    # Handle group lookup
    if module.params.get('assignment_group') and 'assignment_group' in payload:
        value = payload['assignment_group']
        if not (isinstance(value, str) and len(value) == 32 and all(c in '0123456789abcdef' for c in value.lower())):
            payload['assignment_group'] = table_client.get_record(
                'sys_user_group', 
                {'name': module.params['assignment_group']},
                must_exist=True
            )['sys_id']
    
    # Add other parameters
    if module.params.get('other'):
        payload.update(module.params['other'])
    
    return payload


def run(module, table_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, table_client)
    return ensure_present(module, table_client)


def main():
    module_args = dict(
        arguments.get_spec("instance", "sys_id", "number", "attachments", "catalog_request_mapping"),
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        request_state=dict(
            type="str",
            choices=[
                "draft",
                "submitted", 
                "in_process",
                "delivered",
                "cancelled",
                "closed_incomplete",
                "closed_complete",
                "closed_cancelled"
            ],
        ),
        requested_for=dict(type="str"),
        requested_by=dict(type="str"),
        assignment_group=dict(type="str"),
        assigned_to=dict(type="str"),
        priority=dict(
            type="str",
            choices=["1", "2", "3", "4", "5"],
        ),
        urgency=dict(
            type="str", 
            choices=["1", "2", "3"],
        ),
        impact=dict(
            type="str",
            choices=["1", "2", "3"],
        ),
        short_description=dict(type="str"),
        description=dict(type="str"),
        comments=dict(type="str"),
        work_notes=dict(type="str"),
        due_date=dict(type="str"),
        delivery_plan=dict(type="str"),
        delivery_task=dict(type="str"),
        stage=dict(
            type="str",
            choices=["request_approved", "fulfillment", "delivery", "completed"],
        ),
        approval=dict(
            type="str",
            choices=["requested", "approved", "rejected", "not_requested"],
        ),
        other=dict(type="dict"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("sys_id", "number"), True),
        ],
    )

    try:
        snow_client = client.Client(**module.params["instance"])
        table_client = table.TableClient(snow_client)
        changed, record, diff = run(module, table_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ServiceNowError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()