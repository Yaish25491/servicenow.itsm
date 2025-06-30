# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from ansible_collections.servicenow.itsm.plugins.module_utils import errors
from ansible_collections.servicenow.itsm.plugins.modules import catalog_request

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEnsureAbsent:
    def test_delete_catalog_request(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number="REQ0000001",
                sys_id=None,
            )
        )
        table_client.get_record.return_value = dict(
            request_state="submitted", number="REQ0000001", sys_id="1234"
        )

        result = catalog_request.ensure_absent(module, table_client)

        table_client.delete_record.assert_called_once()
        assert result == (
            True,
            dict(request_state="submitted", number="REQ0000001", sys_id="1234"),
            dict(
                before=dict(request_state="submitted", number="REQ0000001", sys_id="1234"),
                after=None,
            ),
        )

    def test_delete_catalog_request_not_present(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number=None,
                sys_id="1234",
            ),
        )
        table_client.get_record.return_value = None

        result = catalog_request.ensure_absent(module, table_client)

        table_client.delete_record.assert_not_called()
        assert result == (False, None, dict(before=None, after=None))


class TestEnsurePresent:
    def test_ensure_present_create_new(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request_state="submitted",
                requested_for="john.doe",
                requested_by="jane.smith",
                short_description="Test catalog request",
                description="Test description",
                priority="2",
                urgency="2",
                impact="3",
            )
        )
        table_client.get_record.side_effect = [
            None,  # catalog request doesn't exist
            {"sys_id": "user123", "user_name": "john.doe"},  # requested_for user lookup
            {"sys_id": "user456", "user_name": "jane.smith"},  # requested_by user lookup
        ]
        table_client.create_record.return_value = dict(
            sys_id="1234",
            number="REQ0000001",
            request_state="submitted",
            requested_for="user123",
            requested_by="user456",
            short_description="Test catalog request",
            description="Test description",
            priority="2",
            urgency="2",
            impact="3",
        )

        result = catalog_request.ensure_present(module, table_client)

        table_client.create_record.assert_called_once()
        assert result[0] is True  # changed
        assert result[1]["number"] == "REQ0000001"
        assert result[2]["before"] is None
        assert result[2]["after"]["number"] == "REQ0000001"

    def test_ensure_present_update_existing(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                number="REQ0000001",
                request_state="in_process",
                work_notes="Starting work on request",
            )
        )
        existing_record = dict(
            sys_id="1234",
            number="REQ0000001",
            request_state="submitted",
            work_notes="",
        )
        updated_record = dict(
            sys_id="1234",
            number="REQ0000001",
            request_state="in_process",
            work_notes="Starting work on request",
        )
        table_client.get_record.return_value = existing_record
        table_client.update_record.return_value = updated_record

        result = catalog_request.ensure_present(module, table_client)

        table_client.update_record.assert_called_once()
        assert result[0] is True  # changed
        assert result[1]["request_state"] == "in_process"
        assert result[2]["before"]["request_state"] == "submitted"
        assert result[2]["after"]["request_state"] == "in_process"

    def test_ensure_present_no_change_needed(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                number="REQ0000001",
                request_state="submitted",
            )
        )
        existing_record = dict(
            sys_id="1234",
            number="REQ0000001",
            request_state="submitted",
        )
        table_client.get_record.return_value = existing_record

        result = catalog_request.ensure_present(module, table_client)

        table_client.update_record.assert_not_called()
        table_client.create_record.assert_not_called()
        assert result[0] is False  # not changed
        assert result[1]["request_state"] == "submitted"


class TestBuildPayload:
    def test_build_payload_simple_fields(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                request_state="submitted",
                short_description="Test request",
                description="Test description",
                priority="2",
                urgency="2",
                impact="3",
                comments="Test comment",
                work_notes="Test work notes",
                due_date="2024-12-31",
                delivery_plan="Standard delivery",
                delivery_task="TASK001",
                stage="request_approved",
                approval="not_requested",
            )
        )

        payload = catalog_request.build_payload(module, table_client)

        expected_fields = {
            "request_state": "submitted",
            "short_description": "Test request",
            "description": "Test description",
            "priority": "2",
            "urgency": "2",
            "impact": "3",
            "comments": "Test comment",
            "work_notes": "Test work notes",
            "due_date": "2024-12-31",
            "delivery_plan": "Standard delivery",
            "delivery_task": "TASK001",
            "stage": "request_approved",
            "approval": "not_requested",
        }
        
        for field, value in expected_fields.items():
            assert payload[field] == value

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

        payload = catalog_request.build_payload(module, table_client)

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

        payload = catalog_request.build_payload(module, table_client)

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
                    business_justification="Required for project",
                    custom_field="custom_value",
                ),
            )
        )

        payload = catalog_request.build_payload(module, table_client)

        assert payload["special_instructions"] == "Handle with care"
        assert payload["business_justification"] == "Required for project"
        assert payload["custom_field"] == "custom_value"

    def test_build_payload_user_lookup_error(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                requested_for="nonexistent.user",
            )
        )
        table_client.get_record.side_effect = errors.ServiceNowError("User not found")

        with pytest.raises(errors.ServiceNowError, match="User not found"):
            catalog_request.build_payload(module, table_client)


class TestRun:
    def test_run_absent(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="absent",
                number="REQ0000001",
            )
        )
        table_client.get_record.return_value = dict(
            sys_id="1234", number="REQ0000001"
        )

        result = catalog_request.run(module, table_client)

        assert result[0] is True  # changed
        table_client.delete_record.assert_called_once()

    def test_run_present(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test request",
            )
        )
        table_client.get_record.return_value = None  # doesn't exist
        table_client.create_record.return_value = dict(
            sys_id="1234", number="REQ0000001", short_description="Test request"
        )

        result = catalog_request.run(module, table_client)

        assert result[0] is True  # changed
        table_client.create_record.assert_called_once()


class TestModuleArguments:
    def test_module_args_state_choices(self):
        # Test that state parameter has correct choices
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.table'):
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

    def test_module_args_request_state_choices(self):
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.table'):
                    try:
                        main()
                    except:
                        pass
            
            call_args = mock_module.call_args
            if call_args:
                arg_spec = call_args[1]['argument_spec']
                assert 'request_state' in arg_spec
                expected_choices = [
                    "draft", "submitted", "in_process", "delivered", 
                    "cancelled", "closed_incomplete", "closed_complete", "closed_cancelled"
                ]
                assert arg_spec['request_state']['choices'] == expected_choices

    def test_module_args_priority_choices(self):
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.table'):
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
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.table'):
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
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test request",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.client.Client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.table.TableClient', return_value=table_client):
                    table_client.get_record.return_value = None
                    table_client.create_record.return_value = dict(
                        sys_id="1234", number="REQ0000001", short_description="Test request"
                    )
                    
                    catalog_request.main()
                    
                    mock_module.exit_json.assert_called_once()
                    call_args = mock_module.exit_json.call_args[1]
                    assert call_args['changed'] is True
                    assert call_args['record']['number'] == "REQ0000001"

    def test_main_servicenow_error(self, create_module):
        """Test error handling in main function"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test request",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request.client.Client') as mock_client:
                mock_client.side_effect = errors.ServiceNowError("Connection failed")
                
                catalog_request.main()
                
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

        payload = catalog_request.build_payload(module, table_client)
        
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
                requested_for=None,
            )
        )

        payload = catalog_request.build_payload(module, table_client)
        
        assert payload["short_description"] == "Test"
        assert "description" not in payload
        assert "priority" not in payload
        assert "requested_for" not in payload

    def test_check_mode_create(self, create_module, table_client):
        """Test check mode for creating new record"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                state="present",
                short_description="Test request",
            ),
            check_mode=True
        )
        table_client.get_record.return_value = None
        table_client.create_record.return_value = dict(
            sys_id="1234", number="REQ0000001", short_description="Test request"
        )

        result = catalog_request.ensure_present(module, table_client)

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
                number="REQ0000001",
            ),
            check_mode=True
        )
        table_client.get_record.return_value = dict(
            sys_id="1234", number="REQ0000001"
        )

        result = catalog_request.ensure_absent(module, table_client)

        table_client.delete_record.assert_called_once()
        # Verify check_mode was passed to delete_record
        call_args = table_client.delete_record.call_args
        assert call_args[1]['check_mode'] is True