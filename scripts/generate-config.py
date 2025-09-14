#!/usr/bin/env python3
"""
Configuration Generator for Retail Gateway Platform
Generates personalized configuration files for installer packages
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib
import uuid

class ConfigGenerator:
    """Generate personalized configuration files for installers"""
    
    def __init__(self, installer_dir: str):
        self.installer_dir = Path(installer_dir)
        self.configs_dir = self.installer_dir / "configs"
        self.packages_dir = self.installer_dir / "packages"
        
    def generate_hardware_fingerprint(self) -> str:
        """Generate a hardware fingerprint for the system"""
        try:
            import platform
            import subprocess
            
            # Get system information
            system_info = {
                'platform': platform.platform(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node()
            }
            
            # Try to get MAC address
            try:
                if sys.platform == "win32":
                    result = subprocess.run(['getmac', '/fo', 'csv'], 
                                          capture_output=True, text=True)
                    mac_address = result.stdout.split('\n')[1].split(',')[0].strip('"')
                else:
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                    # Simple MAC extraction (this is basic - in production use proper parsing)
                    mac_address = "00:00:00:00:00:00"  # Placeholder
            except:
                mac_address = "00:00:00:00:00:00"
            
            system_info['mac_address'] = mac_address
            
            # Create fingerprint
            fingerprint_data = json.dumps(system_info, sort_keys=True)
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            print(f"Warning: Could not generate hardware fingerprint: {e}")
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def generate_license_key(self, client_id: str) -> str:
        """Generate a license key for the client"""
        timestamp = datetime.now().isoformat()
        data = f"{client_id}:{timestamp}:license"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_digital_signature(self, license_key: str, hardware_fingerprint: str) -> str:
        """Generate a digital signature"""
        data = f"{license_key}:{hardware_fingerprint}:signature"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_encryption_key(self) -> str:
        """Generate an encryption key"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def load_template(self, template_name: str) -> dict:
        """Load a configuration template"""
        template_path = self.configs_dir / f"{template_name}.json"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def replace_template_variables(self, template: dict, variables: dict) -> dict:
        """Replace template variables with actual values"""
        template_str = json.dumps(template)
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            # Handle boolean values properly
            if isinstance(value, bool):
                replacement = str(value).lower()
            else:
                replacement = str(value)
            template_str = template_str.replace(placeholder, replacement)
        
        return json.loads(template_str)
    
    def generate_license_config(self, client_info: dict) -> dict:
        """Generate a personalized license configuration"""
        # Load license template
        license_template = self.load_template("license-template")
        
        # Generate security keys
        hardware_fingerprint = self.generate_hardware_fingerprint()
        license_key = self.generate_license_key(client_info['client_id'])
        digital_signature = self.generate_digital_signature(license_key, hardware_fingerprint)
        encryption_key = self.generate_encryption_key()
        
        # Prepare variables
        variables = {
            'LICENSE_KEY': license_key,
            'LICENSE_TYPE': client_info.get('license_type', 'professional'),
            'MAX_LANES': client_info.get('max_lanes', 10),
            'SDK_INTEGRATION': str(client_info.get('sdk_integration', True)).lower(),
            'SESSION_MANAGEMENT': str(client_info.get('session_management', True)).lower(),
            'ANALYTICS_API': str(client_info.get('analytics_api', True)).lower(),
            'ADVANCED_MONITORING': str(client_info.get('advanced_monitoring', True)).lower(),
            'STREAMING_PIPELINE': str(client_info.get('streaming_pipeline', True)).lower(),
            'GRACE_PERIOD_DAYS': client_info.get('grace_period_days', 7),
            'AUTO_RENEWAL': str(client_info.get('auto_renewal', True)).lower(),
            'BILLING_CYCLE': client_info.get('billing_cycle', 'monthly'),
            'HARDWARE_FINGERPRINT': hardware_fingerprint,
            'DIGITAL_SIGNATURE': digital_signature,
            'ENCRYPTION_KEY': encryption_key,
            'CLIENT_ID': client_info['client_id'],
            'CLIENT_NAME': client_info['client_name'],
            'LOCATION': client_info.get('location', ''),
            'PRIMARY_CONTACT': client_info.get('primary_contact', ''),
            'EMAIL': client_info.get('email', ''),
            'PHONE': client_info.get('phone', ''),
            'TECHNICAL_CONTACT': client_info.get('technical_contact', ''),
            'TECHNICAL_EMAIL': client_info.get('technical_email', ''),
            'INSTALL_DATE': datetime.now().isoformat(),
            'INSTALL_PATH': client_info.get('install_path', 'C:\\Program Files\\GulfCoast\\Gateway'),
            'SERVICE_NAME': client_info.get('service_name', 'GulfCoastGateway'),
            'VERSION': client_info.get('version', '1.0.0')
        }
        
        return self.replace_template_variables(license_template, variables)
    
    def generate_service_config(self, client_info: dict, license_config: dict) -> dict:
        """Generate a personalized service configuration"""
        # Load config template
        config_template = self.load_template("config-template")
        
        # Prepare variables
        variables = {
            'GATEWAY_ID': f"gateway_{client_info['client_id']}",
            'VERSION': client_info.get('version', '1.0.0'),
            'LOCATION': client_info.get('location', ''),
            'CLIENT_NAME': client_info['client_name'],
            'STREAMING_PIPELINE_ENABLED': str(client_info.get('streaming_pipeline_enabled', True)).lower(),
            'LAN_IP': client_info.get('lan_ip', '192.168.1.10'),
            'CLIENT_ID': client_info['client_id'],
            'PRIMARY_CONTACT': client_info.get('primary_contact', ''),
            'EMAIL': client_info.get('email', ''),
            'PHONE': client_info.get('phone', ''),
            'TECHNICAL_CONTACT': client_info.get('technical_contact', ''),
            'TECHNICAL_EMAIL': client_info.get('technical_email', ''),
            'SERVICE_NAME': client_info.get('service_name', 'GulfCoastGateway'),
            'INSTALL_PATH': client_info.get('install_path', 'C:\\Program Files\\GulfCoast\\Gateway'),
            'LOG_PATH': client_info.get('log_path', 'C:\\Program Files\\GulfCoast\\Gateway\\logs'),
            'DATA_PATH': client_info.get('data_path', 'C:\\Program Files\\GulfCoast\\Gateway\\data'),
            'BACKUP_PATH': client_info.get('backup_path', 'C:\\Program Files\\GulfCoast\\Gateway\\backup'),
            'LAN_IP_RANGE': client_info.get('lan_ip_range', '192.168.1.0/24'),
            'CONFIGURED_AT': datetime.now().isoformat(),
            'CONFIGURED_BY': client_info.get('configured_by', 'system'),
            # License information
            'LICENSE_KEY': license_config['license_key'],
            'LICENSE_TYPE': license_config['license_type'],
            'MAX_LANES': license_config['max_lanes'],
            'SDK_INTEGRATION': str(license_config['features']['sdk_integration']).lower(),
            'SESSION_MANAGEMENT': str(license_config['features']['session_management']).lower(),
            'ANALYTICS_API': str(license_config['features']['analytics_api']).lower(),
            'ADVANCED_MONITORING': str(license_config['features']['advanced_monitoring']).lower(),
            'STREAMING_PIPELINE': str(license_config['features']['streaming_pipeline']).lower(),
            'GRACE_PERIOD_DAYS': license_config['grace_period_days'],
            'AUTO_RENEWAL': str(license_config['auto_renewal']).lower(),
            'BILLING_CYCLE': license_config['billing_cycle'],
            'HARDWARE_FINGERPRINT': license_config['security']['hardware_fingerprint'],
            'DIGITAL_SIGNATURE': license_config['security']['digital_signature'],
            'ENCRYPTION_KEY': license_config['security']['encryption_key']
        }
        
        return self.replace_template_variables(config_template, variables)
    
    def save_config(self, config: dict, filename: str, output_dir: Path = None) -> Path:
        """Save configuration to file"""
        if output_dir is None:
            output_dir = self.configs_dir
        
        output_path = output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return output_path
    
    def generate_personalized_configs(self, client_info: dict) -> dict:
        """Generate personalized configuration files for a client"""
        print(f"🔧 Generating personalized configs for client: {client_info['client_name']}")
        
        # Generate license configuration
        license_config = self.generate_license_config(client_info)
        license_path = self.save_config(license_config, f"license-{client_info['client_id']}.json")
        print(f"✅ License config saved: {license_path}")
        
        # Generate service configuration
        service_config = self.generate_service_config(client_info, license_config)
        service_path = self.save_config(service_config, f"config-{client_info['client_id']}.json")
        print(f"✅ Service config saved: {service_path}")
        
        return {
            'license_config': license_config,
            'service_config': service_config,
            'license_path': license_path,
            'service_path': service_path
        }

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python generate-config.py <installer_dir> [client_info.json]")
        sys.exit(1)
    
    installer_dir = sys.argv[1]
    
    # Default client info for testing
    default_client_info = {
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
    
    # Load client info from file if provided
    if len(sys.argv) > 2:
        client_info_path = sys.argv[2]
        with open(client_info_path, 'r') as f:
            client_info = json.load(f)
    else:
        client_info = default_client_info
    
    # Generate configurations
    generator = ConfigGenerator(installer_dir)
    result = generator.generate_personalized_configs(client_info)
    
    print("🎉 Personalized configurations generated successfully!")
    print(f"📁 License config: {result['license_path']}")
    print(f"📁 Service config: {result['service_path']}")

if __name__ == "__main__":
    main()
