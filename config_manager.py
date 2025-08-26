"""
Configuration Manager for Payroll System
Manages JSON configuration file for storing paths and settings
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages application configuration stored in JSON file"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize configuration manager
        
        Args:
            config_file: Path to configuration JSON file
        """
        self.config_file = config_file
        self.config_path = Path(config_file)
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                # Create default configuration if file doesn't exist
                self._config = self._get_default_config()
                self.save_config()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            "google_credentials_file": "takefinace-1648e5de7102.json",
            "google_file_id": "",
            "google_folder_id": "",
            "csv_folder_id": "",
            "default_sheet_name": None,
            "processing_settings": {
                "force_recreate": False,
                "generate_csv": True,
                "cleanup_old_sessions_days": 30
            },
            "pdf_settings": {
                "company_name": "TakeFinance",
                "default_currency": "USD",
                "date_format": "%Y-%m-%d"
            },
            "paths": {
                "status_file": "processing_status.json",
                "temp_directory": "temp",
                "logs_directory": "logs"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation like 'processing_settings.force_recreate')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._config:
            return default
        
        # Support dot notation for nested keys
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        if not self._config:
            self._config = self._get_default_config()
        
        # Support dot notation for nested keys
        keys = key.split('.')
        config_ref = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        # Set the final key
        config_ref[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        for key, value in updates.items():
            self.set(key, value)
    
    def save_config(self) -> None:
        """Save current configuration to JSON file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config file: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary
        
        Returns:
            Complete configuration dictionary
        """
        return self._config.copy() if self._config else {}
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = self._get_default_config()
        self.save_config()
    
    # Convenience methods for common configuration values
    def get_google_credentials_file(self) -> str:
        """Get Google credentials file path"""
        return self.get('google_credentials_file', 'takefinace-1648e5de7102.json')
    
    def get_google_file_id(self) -> str:
        """Get Google Sheets file ID"""
        return self.get('google_file_id', '')
    
    def get_google_folder_id(self) -> str:
        """Get Google Drive folder ID for PDFs"""
        return self.get('google_folder_id', '')
    
    def get_csv_folder_id(self) -> str:
        """Get Google Drive folder ID for CSV reports"""
        return self.get('csv_folder_id', '')
    
    def get_default_sheet_name(self) -> Optional[str]:
        """Get default sheet name"""
        return self.get('default_sheet_name')
    
    def get_status_file_path(self) -> str:
        """Get processing status file path"""
        return self.get('paths.status_file', 'processing_status.json')
    
    def should_force_recreate(self) -> bool:
        """Check if force recreate is enabled"""
        return self.get('processing_settings.force_recreate', False)
    
    def should_generate_csv(self) -> bool:
        """Check if CSV generation is enabled"""
        return self.get('processing_settings.generate_csv', True)
    
    def get_company_name(self) -> str:
        """Get company name for PDFs"""
        return self.get('pdf_settings.company_name', 'TakeFinance')
    
    def get_cleanup_days(self) -> int:
        """Get number of days for session cleanup"""
        return self.get('processing_settings.cleanup_old_sessions_days', 30)
    
    def get_sla_descriptions_file_id(self) -> str:
        """Get SLA descriptions spreadsheet file ID"""
        return self.get('sla_descriptions_file_id', '')

# Global configuration instance
config = ConfigManager()
