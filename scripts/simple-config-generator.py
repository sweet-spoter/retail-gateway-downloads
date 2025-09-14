#!/usr/bin/env python3
"""
Simple Configuration Generator for Retail Gateway Platform
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib
import uuid

def generate_hardware_fingerprint():
    """Generate a hardware fingerprint for the system"""
    try:
        import platform
        system_info = {
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node()
        }
        fingerprint_data = json.dumps(system_info, sort_keys=True)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    except Exception as e:
        print(f"Warning: Could not generate hardware fingerprint: {e}")
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def generate_license_key(client_id):
    """Generate a license key for the client"""
    timestamp = datetime.now().isoformat()
    data = f"{client_id}:{timestamp}:license"
    return hashlib.sha256(data.encode()).hexdigest()

def generate_digital_signature(license_key, hardware_fingerprint):
    """Generate a digital signature"""
    data = f"{license_key}:{hardware_fingerprint}:signature"
    return hashlib.sha256(data.encode()).hexdigest()

def generate_encryption_key():
    """Generate an encryption key"""
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def create_license_config(client_info):
    """Create a license configuration"""
    hardware_fingerprint = generate_hardware_fingerprint()
    license_key = generate_license_key(client_info['client_id'])
    digital_signature = generate_digital_signature(license_key, hardware_fingerprint)
    encryption_key = generate_encryption_key()
    
    license_config = {
        "license_key": license_key,
        "license_type": client_info.get('license_type', 'professional'),
        "max_lanes": client_info.get('max_lanes', 10),
        "features": {
            "sdk_integration": client_info.get('sdk_integration', True),
            "session_management": client_info.get('session_management', True),
            "analytics_api": client_info.get('analytics_api', True),
            "advanced_monitoring": client_info.get('advanced_monitoring', True),
            "streaming_pipeline": client_info.get('streaming_pipeline', True),
            "offline_capable": True
        },
        "grace_period_days": client_info.get('grace_period_days', 7),
        "auto_renewal": client_info.get('auto_renewal', True),
        "billing_cycle": client_info.get('billing_cycle', 'monthly'),
        "security": {
            "hardware_fingerprint": hardware_fingerprint,
            "digital_signature": digital_signature,
            "encryption_key": encryption_key,
            "offline_validation": True,
            "license_file_path": "license.json"
        },
        "client_info": {
            "client_id": client_info['client_id'],
            "client_name": client_info['client_name'],
            "location": client_info.get('location', ''),
            "contact_info": {
                "primary_contact": client_info.get('primary_contact', ''),
                "email": client_info.get('email', ''),
                "phone": client_info.get('phone', ''),
                "technical_contact": client_info.get('technical_contact', ''),
                "technical_email": client_info.get('technical_email', '')
            }
        },
        "installation_info": {
            "install_date": datetime.now().isoformat(),
            "install_path": client_info.get('install_path', 'C:\\Program Files\\GulfCoast\\Gateway'),
            "service_name": client_info.get('service_name', 'GulfCoastGateway'),
            "version": client_info.get('version', '1.0.0')
        }
    }
    
    return license_config

def create_service_config(client_info, license_config):
    """Create a service configuration"""
    service_config = {
        "gateway": {
            "id": f"gateway_{client_info['client_id']}",
            "version": client_info.get('version', '1.0.0'),
            "location": client_info.get('location', ''),
            "client": client_info['client_name'],
            "streaming_pipeline_enabled": client_info.get('streaming_pipeline_enabled', True),
            "lan_ip": client_info.get('lan_ip', '192.168.1.10')
        },
        "client_config": {
            "client_id": client_info['client_id'],
            "client_name": client_info['client_name'],
            "location": client_info.get('location', ''),
            "contact_info": {
                "primary_contact": client_info.get('primary_contact', ''),
                "email": client_info.get('email', ''),
                "phone": client_info.get('phone', ''),
                "technical_contact": client_info.get('technical_contact', ''),
                "technical_email": client_info.get('technical_email', '')
            },
            "installation_config": {
                "service_name": client_info.get('service_name', 'GulfCoastGateway'),
                "startup_type": "automatic",
                "install_path": client_info.get('install_path', 'C:\\Program Files\\GulfCoast\\Gateway'),
                "log_path": client_info.get('log_path', 'C:\\Program Files\\GulfCoast\\Gateway\\logs'),
                "data_path": client_info.get('data_path', 'C:\\Program Files\\GulfCoast\\Gateway\\data'),
                "backup_path": client_info.get('backup_path', 'C:\\Program Files\\GulfCoast\\Gateway\\backup')
            },
            "network_config": {
                "lan_ip_range": client_info.get('lan_ip_range', '192.168.1.0/24'),
                "required_ports": [8080, 5999, 4376, 9000],
                "firewall_rules": ["allow_8080", "allow_5999", "allow_4376", "allow_9000"],
                "proxy_config": {
                    "enabled": False,
                    "proxy_url": "",
                    "proxy_credentials": ""
                }
            },
            "system_requirements": {
                "min_ram": "4GB",
                "min_disk_space": "10GB",
                "os_requirements": ["Windows 10", "Windows Server 2016"],
                "dotnet_version": "6.0",
                "python_version": "3.8"
            },
            "installation_status": {
                "configured_by_employee": True,
                "configured_at": datetime.now().isoformat(),
                "configured_by": client_info.get('configured_by', 'system'),
                "installation_ready": True,
                "installation_completed": False,
                "installation_date": None
            }
        },
        "licensing": license_config,
        "monitoring": {
            "health_check_interval": 30,
            "metrics_collection": True,
            "log_level": "INFO"
        }
    }
    
    return service_config

def main():
    """Main function"""
    # Default client info for testing
    client_info = {
        "client_id": "client_001",
        "client_name": "Casino Royale",
        "location": "Las Vegas, NV",
        "primary_contact": "John Doe",
        "email": "john@casinoroyale.com",
        "phone": "+1-555-0123",
        "technical_contact": "Jane Smith",
        "technical_email": "jane@casinoroyale.com",
        "license_type": "professional",
        "max_lanes": 10,
        "sdk_integration": True,
        "session_management": True,
        "analytics_api": True,
        "advanced_monitoring": True,
        "streaming_pipeline": True,
        "grace_period_days": 7,
        "auto_renewal": True,
        "billing_cycle": "monthly",
        "streaming_pipeline_enabled": True,
        "lan_ip": "192.168.1.10",
        "service_name": "GulfCoastGateway",
        "install_path": "C:\\Program Files\\GulfCoast\\Gateway",
        "log_path": "C:\\Program Files\\GulfCoast\\Gateway\\logs",
        "data_path": "C:\\Program Files\\GulfCoast\\Gateway\\data",
        "backup_path": "C:\\Program Files\\GulfCoast\\Gateway\\backup",
        "lan_ip_range": "192.168.1.0/24",
        "configured_by": "system"
    }
    
    print(f"🔧 Generating personalized configs for client: {client_info['client_name']}")
    
    # Generate license configuration
    license_config = create_license_config(client_info)
    license_path = Path("configs") / f"license-{client_info['client_id']}.json"
    license_path.parent.mkdir(exist_ok=True)
    
    with open(license_path, 'w') as f:
        json.dump(license_config, f, indent=2)
    print(f"✅ License config saved: {license_path}")
    
    # Generate service configuration
    service_config = create_service_config(client_info, license_config)
    service_path = Path("configs") / f"config-{client_info['client_id']}.json"
    
    with open(service_path, 'w') as f:
        json.dump(service_config, f, indent=2)
    print(f"✅ Service config saved: {service_path}")
    
    print("🎉 Personalized configurations generated successfully!")

if __name__ == "__main__":
    main()
