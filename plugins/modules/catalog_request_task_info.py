#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: catalog_request_task_info

author:
  - ServiceNow ITSM Collection Contributors

short_description: List ServiceNow catalog request tasks

description:
  - Retrieve information about ServiceNow catalog request tasks (sc_task).
  - For more information, refer to the ServiceNow service catalog documentation at
    U(https://docs.servicenow.com/bundle/utah-servicenow-platform/page/product/service-catalog/concept/c_ServiceCatalogProcess.html).

version_added: 2.7.0

extends_documentation_fragment:
  - servicenow.itsm.instance
  - servicenow.itsm.sys_id.info
  - servicenow.itsm.number.info
  - servicenow.itsm.query
  - servicenow.itsm.sysparm_display_value

seealso:
  - module: servicenow.itsm.catalog_request_task
  - module: servicenow.itsm.catalog_request_info
"""

EXAMPLES = r"""
- name: Retrieve all catalog request tasks
  servicenow.itsm.catalog_request_task_info:
  register: result

- name: Retrieve a specific catalog request task by its sys_id
  servicenow.itsm.catalog_request_task_info:
    sys_id: 471bfbc7a9fe198101e77a3e10e5d47f
  register: result

- name: Retrieve catalog request tasks by number
  servicenow.itsm.catalog_request_task_info:
    number: SCTASK0007601
  register: result

- name: Retrieve catalog request tasks for a specific request
  servicenow.itsm.catalog_request_task_info:
    query:
      - request: = REQ0000123
  register: result

- name: Retrieve catalog request tasks by state
  servicenow.itsm.catalog_request_task_info:
    query:
      - state: = open
  register: result

- name: Retrieve catalog request tasks assigned to specific user
  servicenow.itsm.catalog_request_task_info:
    query:
      - assigned_to: = john.doe
  register: result

- name: Retrieve catalog request tasks assigned to specific group
  servicenow.itsm.catalog_request_task_info:
    query:
      - assignment_group: = IT Support
  register: result

- name: Retrieve catalog request tasks with high priority
  servicenow.itsm.catalog_request_task_info:
    query:
      - priority: = 1
  register: result

- name: Retrieve catalog request tasks using sysparm_query
  servicenow.itsm.catalog_request_task_info:
    sysparm_query: state=open^priority=1
  register: result
"""

RETURN = r"""
records:
  description:
    - A list of catalog request task records.
  returned: success
  type: list
  sample:
    - "active": "true"
      "approval": "not_requested"
      "assigned_to": "john.doe"
      "assignment_group": "IT Support"
      "attachments": []
      "close_notes": ""
      "comments": ""
      "delivery_plan": ""
      "delivery_task": ""
      "description": "Install required software and configure user settings"
      "due_date": ""
      "impact": "3"
      "number": "SCTASK0000456"
      "opened_at": "2024-01-15 10:30:00"
      "opened_by": "jane.smith"
      "order": 10
      "priority": "2"
      "request": "REQ0000123"
      "requested_by": "jane.smith"
      "requested_for": "john.doe"
      "short_description": "Configure new laptop"
      "state": "open"
      "sys_created_by": "jane.smith"
      "sys_created_on": "2024-01-15 10:30:00"
      "sys_id": "c36d93a37b1200001c9c9b5b8a9619a9"
      "sys_updated_by": "jane.smith"
      "sys_updated_on": "2024-01-15 10:30:00"
      "urgency": "2"
      "work_notes": ""
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, client, errors, table


def run(module, table_client):
    query = {}
    if module.params.get("sys_id"):
        query["sys_id"] = module.params["sys_id"]
    if module.params.get("number"):
        query["number"] = module.params["number"]

    return table_client.list_records(
        "sc_task",
        query,
        sysparm_query=module.params.get("sysparm_query"),
        sysparm_display_value=module.params.get("sysparm_display_value"),
    )


def main():
    module_args = dict(
        arguments.get_spec("instance", "sys_id", "number", "query", "sysparm_display_value"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        snow_client = client.Client(**module.params["instance"])
        table_client = table.TableClient(snow_client)
        records = run(module, table_client)
        module.exit_json(changed=False, records=records)
    except errors.ServiceNowError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()