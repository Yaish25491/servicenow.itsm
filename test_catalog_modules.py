#!/usr/bin/env python3

"""Simple test script to verify catalog modules load correctly"""

import sys
import os

# Add the collection path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    # Test importing catalog_request
    from ansible_collections.servicenow.itsm.plugins.modules import catalog_request
    print("✓ catalog_request module imported successfully")
    
    # Test importing catalog_request_task
    from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task
    print("✓ catalog_request_task module imported successfully")
    
    # Test importing catalog_request_info
    from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_info
    print("✓ catalog_request_info module imported successfully")
    
    # Test importing catalog_request_task_info
    from ansible_collections.servicenow.itsm.plugins.modules import catalog_request_task_info
    print("✓ catalog_request_task_info module imported successfully")
    
    # Test importing module utils
    from ansible_collections.servicenow.itsm.plugins.module_utils import catalog_request as cr_utils
    print("✓ catalog_request module_utils imported successfully")
    
    from ansible_collections.servicenow.itsm.plugins.module_utils import catalog_request_task as crt_utils
    print("✓ catalog_request_task module_utils imported successfully")
    
    # Test PAYLOAD_FIELDS_MAPPING exists
    assert hasattr(cr_utils, 'PAYLOAD_FIELDS_MAPPING'), "catalog_request missing PAYLOAD_FIELDS_MAPPING"
    assert hasattr(crt_utils, 'PAYLOAD_FIELDS_MAPPING'), "catalog_request_task missing PAYLOAD_FIELDS_MAPPING"
    print("✓ PAYLOAD_FIELDS_MAPPING found in both module_utils")
    
    print("\n🎉 All catalog modules are ready!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)