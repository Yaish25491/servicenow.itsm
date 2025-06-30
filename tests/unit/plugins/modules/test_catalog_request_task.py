# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from ansible_collections.servicenow.itsm.plugins.module_utils import errors
from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEnsureAbsent:
    def test_delete_catalog_request_task(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number="SCTASK0000001",
                sys_id=None,
            )
        )
        table_client.get_record.return_value = dict(
            state="open", number="SCTASK0000001", sys_id="1234"
        )

        result = catalog_request_task.ensure_absent(module, table_client)

        table_client.delete_record.assert_called_once()
        assert result == (
            True,
            dict(state="open", number="SCTASK0000001", sys_id="1234"),
            dict(
                before=dict(state="open", number="SCTASK0000001", sys_id="1234"),
                after=None,
            ),
        )

    def test_delete_catalog_request_task_not_present(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number=None,
                sys_id="1234",
            ),
        )
        table_client.get_record.return_value = None

        result = catalog_request_task.ensure_absent(module, table_client)

        table_client.delete_record.assert_not_called()
        assert result == (False, None, dict(before=None, after=None))


class TestEnsurePresent:
    def test_ensure_present_create_new(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="REQ0000001",
                task_state="open",
                short_description="Configure laptop",
                description="Install software and configure settings",
                assignment_group="IT Support",
                priority="2",
                urgency="2",
                impact="3",
                order=10,
            )
        )
        table_client.get_record.side_effect = [
            None,  # catalog request task doesn't exist
            {"sys_id": "req123", "number": "REQ0000001"},  # request lookup
            {"sys_id": "group123", "name": "IT Support"},  # assignment_group lookup
        ]
        table_client.create_record.return_value = dict(
            sys_id="1234",
            number="SCTASK0000001",
            request="req123",
            state="open",
            short_description="Configure laptop",
            description="Install software and configure settings",
            assignment_group="group123",
            priority="2",
            urgency="2",
            impact="3",
            order=10,
        )

        result = catalog_request_task.ensure_present(module, table_client)

        table_client.create_record.assert_called_once()
        assert result[0] is True  # changed
        assert result[1]["number"] == "SCTASK0000001"
        assert result[2]["before"] is None
        assert result[2]["after"]["number"] == "SCTASK0000001"

    def test_ensure_present_update_existing(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                number="SCTASK0000001",
                task_state="work_in_progress",
                assigned_to="john.doe",
                work_notes="Started working on task",
            )
        )
        existing_record = dict(
            sys_id="1234",
            number="SCTASK0000001",
            state="open",
            assigned_to="",
            work_notes="",
        )
        updated_record = dict(
            sys_id="1234",
            number="SCTASK0000001",
            state="work_in_progress",
            assigned_to="user123",
            work_notes="Started working on task",
        )
        table_client.get_record.side_effect = [
            existing_record,  # task exists
            {"sys_id": "user123", "user_name": "john.doe"},  # assigned_to lookup
        ]
        table_client.update_record.return_value = updated_record

        result = catalog_request_task.ensure_present(module, table_client)

        table_client.update_record.assert_called_once()
        assert result[0] is True  # changed
        assert result[1]["state"] == "work_in_progress"
        assert result[2]["before"]["state"] == "open"
        assert result[2]["after"]["state"] == "work_in_progress"

    def test_ensure_present_no_change_needed(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                number="SCTASK0000001",
                task_state="open",
            )
        )
        existing_record = dict(
            sys_id="1234",
            number="SCTASK0000001",
            state="open",
        )
        table_client.get_record.return_value = existing_record

        result = catalog_request_task.ensure_present(module, table_client)

        table_client.update_record.assert_not_called()
        table_client.create_record.assert_not_called()
        assert result[0] is False  # not changed
        assert result[1]["state"] == "open"


class TestBuildPayload:
    def test_build_payload_simple_fields(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                task_state="open",
                short_description="Test task",
                description="Test description",
                priority="2",
                urgency="2",
                impact="3",
                comments="Test comment",
                work_notes="Test work notes",
                due_date="2024-12-31",
                close_notes="Task completed",
                order=5,
                approval="not_requested",
                delivery_plan="Standard delivery",
                delivery_task="TASK001",
            )
        )

        payload = catalog_request_task.build_payload(module, table_client)

        expected_fields = {
            "state": "open",
            "short_description": "Test task",
            "description": "Test description",
            "priority": "2",
            "urgency": "2",
            "impact": "3",
            "comments": "Test comment",
            "work_notes": "Test work notes",
            "due_date": "2024-12-31",
            "close_notes": "Task completed",
            "order": 5,
            "approval": "not_requested",
            "delivery_plan": "Standard delivery",
            "delivery_task": "TASK001",
        }
        
        for field, value in expected_fields.items():
            assert payload[field] == value

    def test_build_payload_request_lookup_by_sys_id(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="a1b2c3d4e5f6789012345678901234ab",  # 32-char hex sys_id
            )
        )
        table_client.get_record.return_value = {
            "sys_id": "a1b2c3d4e5f6789012345678901234ab",
            "number": "REQ0000001"
        }

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["request"] == "a1b2c3d4e5f6789012345678901234ab"
        table_client.get_record.assert_called_once_with(
            'sc_request', 
            {'sys_id': 'a1b2c3d4e5f6789012345678901234ab'}, 
            must_exist=True
        )

    def test_build_payload_request_lookup_by_number(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="REQ0000001",
            )
        )
        table_client.get_record.return_value = {
            "sys_id": "req123",
            "number": "REQ0000001"
        }

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["request"] == "req123"
        table_client.get_record.assert_called_once_with(
            'sc_request', 
            {'number': 'REQ0000001'}, 
            must_exist=True
        )

    def test_build_payload_user_lookups(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                requested_for="john.doe",
                requested_by="jane.smith",
                assigned_to="admin",
            )
        )
        table_client.get_record.side_effect = [
            {"sys_id": "user123", "user_name": "john.doe"},  # requested_for
            {"sys_id": "user456", "user_name": "jane.smith"},  # requested_by
            {"sys_id": "user789", "user_name": "admin"},  # assigned_to
        ]

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["requested_for"] == "user123"
        assert payload["requested_by"] == "user456"
        assert payload["assigned_to"] == "user789"

        # Verify correct user lookups were called
        assert table_client.get_record.call_count == 3
        table_client.get_record.assert_any_call(
            'sys_user', {'user_name': 'john.doe'}, must_exist=True
        )
        table_client.get_record.assert_any_call(
            'sys_user', {'user_name': 'jane.smith'}, must_exist=True
        )
        table_client.get_record.assert_any_call(
            'sys_user', {'user_name': 'admin'}, must_exist=True
        )

    def test_build_payload_group_lookup(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                assignment_group="IT Support",
            )
        )
        table_client.get_record.return_value = {
            "sys_id": "group123", 
            "name": "IT Support"
        }

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["assignment_group"] == "group123"
        table_client.get_record.assert_called_once_with(
            'sys_user_group', {'name': 'IT Support'}, must_exist=True
        )

    def test_build_payload_other_parameters(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                other=dict(
                    special_instructions="Handle with care",
                    vendor="Dell",
                    custom_field="custom_value",
                ),
            )
        )

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["special_instructions"] == "Handle with care"
        assert payload["vendor"] == "Dell"
        assert payload["custom_field"] == "custom_value"

    def test_build_payload_request_lookup_error(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="NONEXISTENT001",
            )
        )
        table_client.get_record.side_effect = errors.ServiceNowError("Request not found")

        with pytest.raises(errors.ServiceNowError, match="Request not found"):
            catalog_request_task.build_payload(module, table_client)


class TestRun:
    def test_run_absent(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number="SCTASK0000001",
            )
        )
        table_client.get_record.return_value = dict(
            sys_id="1234", number="SCTASK0000001"
        )

        result = catalog_request_task.run(module, table_client)

        assert result[0] is True  # changed
        table_client.delete_record.assert_called_once()

    def test_run_present(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test task",
            )
        )
        table_client.get_record.return_value = None  # doesn't exist
        table_client.create_record.return_value = dict(
            sys_id="1234", number="SCTASK0000001", short_description="Test task"
        )

        result = catalog_request_task.run(module, table_client)

        assert result[0] is True  # changed
        table_client.create_record.assert_called_once()


class TestModuleArguments:
    def test_module_args_state_choices(self):
        # Test that state parameter has correct choices
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.table'):
                    try:
                        main()
                    except:
                        pass  # We don't care about execution, just argument spec
            
            # Get the argument spec that was passed to AnsibleModule
            call_args = mock_module.call_args
            if call_args:
                arg_spec = call_args[1]['argument_spec']
                assert 'state' in arg_spec
                assert arg_spec['state']['choices'] == ["present", "absent"]
                assert arg_spec['state']['default'] == "present"

    def test_module_args_task_state_choices(self):
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.table'):
                    try:
                        main()
                    except:
                        pass
            
            call_args = mock_module.call_args
            if call_args:
                arg_spec = call_args[1]['argument_spec']
                assert 'task_state' in arg_spec
                expected_choices = [
                    "pending", "open", "work_in_progress", "closed_complete", 
                    "closed_incomplete", "closed_skipped", "closed_cancelled"
                ]
                assert arg_spec['task_state']['choices'] == expected_choices

    def test_module_args_priority_choices(self):
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.table'):
                    try:
                        main()
                    except:
                        pass
            
            call_args = mock_module.call_args
            if call_args:
                arg_spec = call_args[1]['argument_spec']
                assert 'priority' in arg_spec
                assert arg_spec['priority']['choices'] == ["1", "2", "3", "4", "5"]

    def test_module_required_if(self):
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.table'):
                    try:
                        main()
                    except:
                        pass
            
            call_args = mock_module.call_args
            if call_args:
                required_if = call_args[1]['required_if']
                assert ("state", "absent", ("sys_id", "number"), True) in required_if


class TestModuleIntegration:
    def test_main_success(self, create_module, table_client):
        """Test successful execution of main function"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test task",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.client.Client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.table.TableClient', return_value=table_client):
                    table_client.get_record.return_value = None
                    table_client.create_record.return_value = dict(
                        sys_id="1234", number="SCTASK0000001", short_description="Test task"
                    )
                    
                    catalog_request_task.main()
                    
                    mock_module.exit_json.assert_called_once()
                    call_args = mock_module.exit_json.call_args[1]
                    assert call_args['changed'] is True
                    assert call_args['record']['number'] == "SCTASK0000001"

    def test_main_servicenow_error(self, create_module):
        """Test error handling in main function"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test task",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_task.client.Client') as mock_client:
                mock_client.side_effect = errors.ServiceNowError("Connection failed")
                
                catalog_request_task.main()
                
                mock_module.fail_json.assert_called_once_with(msg="Connection failed")


class TestEdgeCases:
    def test_empty_other_parameter(self, create_module, table_client):
        """Test handling of empty other parameter"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                other={},
            )
        )

        payload = catalog_request_task.build_payload(module, table_client)
        
        # Empty other dict should not add any fields
        assert len(payload) == 0

    def test_none_values_excluded(self, create_module, table_client):
        """Test that None values are excluded from payload"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test",
                description=None,
                priority=None,
                request=None,
            )
        )

        payload = catalog_request_task.build_payload(module, table_client)
        
        assert payload["short_description"] == "Test"
        assert "description" not in payload
        assert "priority" not in payload
        assert "request" not in payload

    def test_check_mode_create(self, create_module, table_client):
        """Test check mode for creating new record"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test task",
            ),
            check_mode=True
        )
        table_client.get_record.return_value = None
        table_client.create_record.return_value = dict(
            sys_id="1234", number="SCTASK0000001", short_description="Test task"
        )

        result = catalog_request_task.ensure_present(module, table_client)

        table_client.create_record.assert_called_once()
        # Verify check_mode was passed to create_record
        call_args = table_client.create_record.call_args
        assert call_args[1]['check_mode'] is True

    def test_check_mode_delete(self, create_module, table_client):
        """Test check mode for deleting record"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number="SCTASK0000001",
            ),
            check_mode=True
        )
        table_client.get_record.return_value = dict(
            sys_id="1234", number="SCTASK0000001"
        )

        result = catalog_request_task.ensure_absent(module, table_client)

        table_client.delete_record.assert_called_once()
        # Verify check_mode was passed to delete_record
        call_args = table_client.delete_record.call_args
        assert call_args[1]['check_mode'] is True

    def test_request_sys_id_detection_uppercase(self, create_module, table_client):
        """Test that uppercase hex characters in sys_id are properly detected"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="A1B2C3D4E5F6789012345678901234AB",  # uppercase hex
            )
        )
        table_client.get_record.return_value = {
            "sys_id": "A1B2C3D4E5F6789012345678901234AB",
            "number": "REQ0000001"
        }

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["request"] == "A1B2C3D4E5F6789012345678901234AB"
        table_client.get_record.assert_called_once_with(
            'sc_request', 
            {'sys_id': 'A1B2C3D4E5F6789012345678901234AB'}, 
            must_exist=True
        )

    def test_request_mixed_case_sys_id(self, create_module, table_client):
        """Test that mixed case hex characters in sys_id are properly detected"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="a1B2c3D4e5F6789012345678901234aB",  # mixed case hex
            )
        )
        table_client.get_record.return_value = {
            "sys_id": "a1B2c3D4e5F6789012345678901234aB",
            "number": "REQ0000001"
        }

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["request"] == "a1B2c3D4e5F6789012345678901234aB"
        table_client.get_record.assert_called_once_with(
            'sc_request', 
            {'sys_id': 'a1B2c3D4e5F6789012345678901234aB'}, 
            must_exist=True
        )

    def test_request_not_hex_treated_as_number(self, create_module, table_client):
        """Test that non-hex 32-character strings are treated as numbers"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request="REQ000000000000000000000000000001",  # 32 chars but not hex
            )
        )
        table_client.get_record.return_value = {
            "sys_id": "real_sys_id_123",
            "number": "REQ000000000000000000000000000001"
        }

        payload = catalog_request_task.build_payload(module, table_client)

        assert payload["request"] == "real_sys_id_123"
        table_client.get_record.assert_called_once_with(
            'sc_request', 
            {'number': 'REQ000000000000000000000000000001'}, 
            must_exist=True
        )