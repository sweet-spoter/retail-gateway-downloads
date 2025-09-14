#!/usr/bin/env python3
"""
Simple test script for configuration generation
"""

import json
from pathlib import Path

def test_template_loading():
    """Test loading the license template"""
    configs_dir = Path("configs")
    template_path = configs_dir / "license-template.json"
    
    print(f"Loading template from: {template_path}")
    
    try:
        with open(template_path, 'r') as f:
            template = json.load(f)
        print("✅ Template loaded successfully")
        print(f"Template keys: {list(template.keys())}")
        return template
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return None

def test_simple_replacement():
    """Test simple template replacement"""
    template = {
        "license_key": "{{LICENSE_KEY}}",
        "max_lanes": "{{MAX_LANES}}",
        "features": {
            "sdk_integration": "{{SDK_INTEGRATION}}"
        }
    }
    
    variables = {
        "LICENSE_KEY": "test-key-123",
        "MAX_LANES": "5",
        "SDK_INTEGRATION": "true"
    }
    
    print("Testing simple replacement...")
    template_str = json.dumps(template)
    print(f"Original template: {template_str}")
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        template_str = template_str.replace(placeholder, str(value))
    
    print(f"After replacement: {template_str}")
    
    try:
        result = json.loads(template_str)
        print("✅ Replacement successful")
        print(f"Result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ Error parsing result: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing configuration generation...")
    
    # Test template loading
    template = test_template_loading()
    
    # Test simple replacement
    result = test_simple_replacement()
    
    print("🎉 Test completed!")
