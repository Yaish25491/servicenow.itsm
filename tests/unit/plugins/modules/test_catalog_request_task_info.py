# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from ansible_collections.servicenow.itsm.plugins.module_utils import errors
from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task_info

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_with_sys_id(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id="1234567890abcdef1234567890abcdef",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                short_description="Configure laptop",
                request="REQ0000001",
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {"sys_id": "1234567890abcdef1234567890abcdef"},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 1
        assert result[0]["number"] == "SCTASK0000001"
        assert result[0]["state"] == "open"

    def test_run_with_number(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="SCTASK0000001",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                short_description="Configure laptop",
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {"number": "SCTASK0000001"},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 1
        assert result[0]["number"] == "SCTASK0000001"

    def test_run_with_sysparm_query(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query="state=open^priority=1",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                priority="1",
                short_description="High priority task",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="SCTASK0000002",
                state="open",
                priority="1",
                short_description="Another high priority task",
            ),
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {},
            sysparm_query="state=open^priority=1",
            sysparm_display_value=None,
        )
        assert len(result) == 2
        assert result[0]["priority"] == "1"
        assert result[1]["priority"] == "1"

    def test_run_with_sysparm_display_value(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_display_value="true",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                assigned_to="John Doe",        # Display value instead of sys_id
                assignment_group="IT Support", # Display value instead of sys_id
                request="REQ0000001",          # Display value instead of sys_id
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {},
            sysparm_query=None,
            sysparm_display_value="true",
        )
        assert len(result) == 1
        assert result[0]["assigned_to"] == "John Doe"
        assert result[0]["assignment_group"] == "IT Support"
        assert result[0]["request"] == "REQ0000001"

    def test_run_with_both_sys_id_and_number(self, create_module, table_client):
        """Test that both sys_id and number are included in query when both provided"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {
                "sys_id": "1234567890abcdef1234567890abcdef",
                "number": "SCTASK0000001"
            },
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 1

    def test_run_with_all_parameters(self, create_module, table_client):
        """Test with all query parameters"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                sysparm_query="state=open",
                sysparm_display_value="all",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {
                "sys_id": "1234567890abcdef1234567890abcdef",
                "number": "SCTASK0000001"
            },
            sysparm_query="state=open",
            sysparm_display_value="all",
        )

    def test_run_no_parameters(self, create_module, table_client):
        """Test retrieving all catalog request tasks with no filters"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                short_description="First task",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="SCTASK0000002",
                state="work_in_progress",
                short_description="Second task",
            ),
        ]

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 2
        assert result[0]["number"] == "SCTASK0000001"
        assert result[1]["number"] == "SCTASK0000002"

    def test_run_empty_result(self, create_module, table_client):
        """Test when no records are found"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="NONEXISTENT001",
            )
        )
        table_client.list_records.return_value = []

        result = catalog_request_task_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_task",
            {"number": "NONEXISTENT001"},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 0

    def test_run_filter_by_request(self, create_module, table_client):
        """Test filtering tasks by parent request using sysparm_query"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query="request=REQ0000001",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                request="REQ0000001",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="SCTASK0000002",
                state="work_in_progress",
                request="REQ0000001",
            ),
        ]

        result = catalog_request_task_info.run(module, table_client)

        assert len(result) == 2
        assert all(task["request"] == "REQ0000001" for task in result)

    def test_run_filter_by_assignment_group(self, create_module, table_client):
        """Test filtering tasks by assignment group"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query="assignment_group=IT Support",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                assignment_group="IT Support",
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        assert len(result) == 1
        assert result[0]["assignment_group"] == "IT Support"


class TestModuleArguments:
    def test_module_args_structure(self):
        """Test that module accepts correct argument specification"""
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.table'):
                    try:
                        main()
                    except:
                        pass  # We don't care about execution, just argument spec
            
            # Get the argument spec that was passed to AnsibleModule
            call_args = mock_module.call_args
            if call_args:
                kwargs = call_args[1]
                assert 'argument_spec' in kwargs
                assert 'supports_check_mode' in kwargs
                assert kwargs['supports_check_mode'] is True


class TestModuleIntegration:
    def test_main_success(self, create_module, table_client):
        """Test successful execution of main function"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task_info
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="SCTASK0000001",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.client.Client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.table.TableClient', return_value=table_client):
                    table_client.list_records.return_value = [
                        dict(
                            sys_id="1234567890abcdef1234567890abcdef",
                            number="SCTASK0000001",
                            state="open",
                        )
                    ]
                    
                    catalog_request_task_info.main()
                    
                    mock_module.exit_json.assert_called_once()
                    call_args = mock_module.exit_json.call_args[1]
                    assert call_args['changed'] is False
                    assert len(call_args['records']) == 1
                    assert call_args['records'][0]['number'] == "SCTASK0000001"

    def test_main_servicenow_error(self, create_module):
        """Test error handling in main function"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task_info
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="SCTASK0000001",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.client.Client') as mock_client:
                mock_client.side_effect = errors.ServiceNowError("Connection failed")
                
                catalog_request_task_info.main()
                
                mock_module.fail_json.assert_called_once_with(msg="Connection failed")

    def test_main_table_client_error(self, create_module, table_client):
        """Test error handling when TableClient operations fail"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task_info
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="SCTASK0000001",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.client.Client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task_info.table.TableClient', return_value=table_client):
                    table_client.list_records.side_effect = errors.ServiceNowError("Table access denied")
                    
                    catalog_request_task_info.main()
                    
                    mock_module.fail_json.assert_called_once_with(msg="Table access denied")


class TestQueryBuilding:
    def test_query_with_only_sys_id(self, create_module, table_client):
        """Test query building with only sys_id parameter"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id="1234567890abcdef1234567890abcdef",
                number=None,
            )
        )
        table_client.list_records.return_value = []

        catalog_request_task_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        query = call_args[0][1]  # Second positional argument is the query
        assert query == {"sys_id": "1234567890abcdef1234567890abcdef"}

    def test_query_with_only_number(self, create_module, table_client):
        """Test query building with only number parameter"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id=None,
                number="SCTASK0000001",
            )
        )
        table_client.list_records.return_value = []

        catalog_request_task_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        query = call_args[0][1]  # Second positional argument is the query
        assert query == {"number": "SCTASK0000001"}

    def test_query_with_neither_sys_id_nor_number(self, create_module, table_client):
        """Test query building with neither sys_id nor number"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id=None,
                number=None,
            )
        )
        table_client.list_records.return_value = []

        catalog_request_task_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        query = call_args[0][1]  # Second positional argument is the query
        assert query == {}


class TestTableInteraction:
    def test_correct_table_name(self, create_module, table_client):
        """Test that the correct ServiceNow table name is used"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
            )
        )
        table_client.list_records.return_value = []

        catalog_request_task_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        table_name = call_args[0][0]  # First positional argument is the table name
        assert table_name == "sc_task"

    def test_sysparm_parameters_passed_correctly(self, create_module, table_client):
        """Test that sysparm parameters are passed correctly to table client"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query="test_query",
                sysparm_display_value="test_display",
            )
        )
        table_client.list_records.return_value = []

        catalog_request_task_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        kwargs = call_args[1]
        assert kwargs['sysparm_query'] == "test_query"
        assert kwargs['sysparm_display_value'] == "test_display"

    def test_none_sysparm_parameters(self, create_module, table_client):
        """Test handling of None sysparm parameters"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query=None,
                sysparm_display_value=None,
            )
        )
        table_client.list_records.return_value = []

        catalog_request_task_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        kwargs = call_args[1]
        assert kwargs['sysparm_query'] is None
        assert kwargs['sysparm_display_value'] is None


class TestSpecialScenarios:
    def test_multiple_tasks_for_same_request(self, create_module, table_client):
        """Test retrieving multiple tasks for the same catalog request"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query="request=REQ0000001",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                request="REQ0000001",
                order=1,
                short_description="Task 1",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="SCTASK0000002",
                state="pending",
                request="REQ0000001",
                order=2,
                short_description="Task 2",
            ),
        ]

        result = catalog_request_task_info.run(module, table_client)

        assert len(result) == 2
        assert result[0]["order"] == 1
        assert result[1]["order"] == 2
        assert all(task["request"] == "REQ0000001" for task in result)

    def test_tasks_with_different_states(self, create_module, table_client):
        """Test retrieving tasks with various states"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="SCTASK0000002",
                state="work_in_progress",
            ),
            dict(
                sys_id="fedcba0987654321fedcba0987654321",
                number="SCTASK0000003",
                state="closed_complete",
            ),
        ]

        result = catalog_request_task_info.run(module, table_client)

        assert len(result) == 3
        states = [task["state"] for task in result]
        assert "open" in states
        assert "work_in_progress" in states
        assert "closed_complete" in states

    def test_tasks_with_attachments_and_references(self, create_module, table_client):
        """Test retrieving tasks with complex data including attachments"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_display_value="true",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="SCTASK0000001",
                state="open",
                assigned_to="John Doe",
                assignment_group="IT Support",
                request="REQ0000001",
                attachments=[
                    {
                        "file_name": "config.txt",
                        "size_bytes": "1024",
                        "content_type": "text/plain"
                    }
                ],
                delivery_plan="Standard",
                delivery_task="DTASK001",
            )
        ]

        result = catalog_request_task_info.run(module, table_client)

        assert len(result) == 1
        task = result[0]
        assert task["assigned_to"] == "John Doe"
        assert task["assignment_group"] == "IT Support"
        assert len(task["attachments"]) == 1
        assert task["attachments"][0]["file_name"] == "config.txt"