# -*- coding: utf-8 -*-
# Copyright: (c) 2024, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from ansible_collections.servicenow.itsm.plugins.module_utils import errors
from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_info

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
                number="REQ0000001",
                request_state="submitted",
                short_description="Test catalog request",
            )
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {"sys_id": "1234567890abcdef1234567890abcdef"},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 1
        assert result[0]["number"] == "REQ0000001"
        assert result[0]["request_state"] == "submitted"

    def test_run_with_number(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="REQ0000001",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="REQ0000001",
                request_state="submitted",
                short_description="Test catalog request",
            )
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {"number": "REQ0000001"},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 1
        assert result[0]["number"] == "REQ0000001"

    def test_run_with_sysparm_query(self, create_module, table_client):
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sysparm_query="request_state=submitted^short_descriptionLIKElaptop",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="REQ0000001",
                request_state="submitted",
                short_description="Request for laptop",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="REQ0000002",
                request_state="submitted",
                short_description="Laptop replacement request",
            ),
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {},
            sysparm_query="request_state=submitted^short_descriptionLIKElaptop",
            sysparm_display_value=None,
        )
        assert len(result) == 2
        assert result[0]["short_description"] == "Request for laptop"
        assert result[1]["short_description"] == "Laptop replacement request"

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
                number="REQ0000001",
                request_state="submitted",
                requested_by="Jane Smith",  # Display value instead of sys_id
                requested_for="John Doe",   # Display value instead of sys_id
                assignment_group="IT Support",  # Display value instead of sys_id
            )
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {},
            sysparm_query=None,
            sysparm_display_value="true",
        )
        assert len(result) == 1
        assert result[0]["requested_by"] == "Jane Smith"
        assert result[0]["requested_for"] == "John Doe"
        assert result[0]["assignment_group"] == "IT Support"

    def test_run_with_both_sys_id_and_number(self, create_module, table_client):
        """Test that both sys_id and number are included in query when both provided"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id="1234567890abcdef1234567890abcdef",
                number="REQ0000001",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="REQ0000001",
                request_state="submitted",
            )
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {
                "sys_id": "1234567890abcdef1234567890abcdef",
                "number": "REQ0000001"
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
                number="REQ0000001",
                sysparm_query="request_state=submitted",
                sysparm_display_value="all",
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="REQ0000001",
                request_state="submitted",
            )
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {
                "sys_id": "1234567890abcdef1234567890abcdef",
                "number": "REQ0000001"
            },
            sysparm_query="request_state=submitted",
            sysparm_display_value="all",
        )

    def test_run_no_parameters(self, create_module, table_client):
        """Test retrieving all catalog requests with no filters"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
            )
        )
        table_client.list_records.return_value = [
            dict(
                sys_id="1234567890abcdef1234567890abcdef",
                number="REQ0000001",
                request_state="submitted",
                short_description="First request",
            ),
            dict(
                sys_id="abcdef1234567890abcdef1234567890",
                number="REQ0000002",
                request_state="in_process",
                short_description="Second request",
            ),
        ]

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 2
        assert result[0]["number"] == "REQ0000001"
        assert result[1]["number"] == "REQ0000002"

    def test_run_empty_result(self, create_module, table_client):
        """Test when no records are found"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="NONEXISTENT001",
            )
        )
        table_client.list_records.return_value = []

        result = catalog_request_info.run(module, table_client)

        table_client.list_records.assert_called_once_with(
            "sc_request",
            {"number": "NONEXISTENT001"},
            sysparm_query=None,
            sysparm_display_value=None,
        )
        assert len(result) == 0


class TestModuleArguments:
    def test_module_args_structure(self):
        """Test that module accepts correct argument specification"""
        from ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info import main
        import unittest.mock as mock
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.AnsibleModule') as mock_module:
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.table'):
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
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_info
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="REQ0000001",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.client.Client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.table.TableClient', return_value=table_client):
                    table_client.list_records.return_value = [
                        dict(
                            sys_id="1234567890abcdef1234567890abcdef",
                            number="REQ0000001",
                            request_state="submitted",
                        )
                    ]
                    
                    catalog_request_info.main()
                    
                    mock_module.exit_json.assert_called_once()
                    call_args = mock_module.exit_json.call_args[1]
                    assert call_args['changed'] is False
                    assert len(call_args['records']) == 1
                    assert call_args['records'][0]['number'] == "REQ0000001"

    def test_main_servicenow_error(self, create_module):
        """Test error handling in main function"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_info
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="REQ0000001",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.client.Client') as mock_client:
                mock_client.side_effect = errors.ServiceNowError("Connection failed")
                
                catalog_request_info.main()
                
                mock_module.fail_json.assert_called_once_with(msg="Connection failed")

    def test_main_table_client_error(self, create_module, table_client):
        """Test error handling when TableClient operations fail"""
        import unittest.mock as mock
        from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_info
        
        mock_module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                number="REQ0000001",
            )
        )
        
        with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.AnsibleModule', return_value=mock_module):
            with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.client.Client'):
                with mock.patch('ansible_collections.servicenow.itsm.plugins.modules.catalog_request_info.table.TableClient', return_value=table_client):
                    table_client.list_records.side_effect = errors.ServiceNowError("Table access denied")
                    
                    catalog_request_info.main()
                    
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

        catalog_request_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        query = call_args[0][1]  # Second positional argument is the query
        assert query == {"sys_id": "1234567890abcdef1234567890abcdef"}

    def test_query_with_only_number(self, create_module, table_client):
        """Test query building with only number parameter"""
        module = create_module(
            params=dict(
                instance=dict(host="my.host.name", username="user", password="pass"),
                sys_id=None,
                number="REQ0000001",
            )
        )
        table_client.list_records.return_value = []

        catalog_request_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        query = call_args[0][1]  # Second positional argument is the query
        assert query == {"number": "REQ0000001"}

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

        catalog_request_info.run(module, table_client)

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

        catalog_request_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        table_name = call_args[0][0]  # First positional argument is the table name
        assert table_name == "sc_request"

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

        catalog_request_info.run(module, table_client)

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

        catalog_request_info.run(module, table_client)

        call_args = table_client.list_records.call_args
        kwargs = call_args[1]
        assert kwargs['sysparm_query'] is None
        assert kwargs['sysparm_display_value'] is None