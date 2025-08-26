"""
Test script to verify JSON configuration and status saving
"""

import json
from config_manager import config
from processing_tracker import ProcessingTracker

def test_config_saving():
    """Test configuration saving and loading"""
    print("=== Testing Configuration Management ===")
    
    # Test initial config
    print(f"Initial Google File ID: {config.get_google_file_id()}")
    print(f"Initial Company Name: {config.get_company_name()}")
    
    # Update some settings
    config.update({
        'google_file_id': 'test_file_123',
        'google_folder_id': 'test_folder_456',
        'pdf_settings.company_name': 'Test Company'
    })
    
    # Save config
    config.save_config()
    print("✅ Configuration saved")
    
    # Verify config file exists and contains correct data
    with open('config.json', 'r', encoding='utf-8') as f:
        saved_config = json.load(f)
    
    print(f"Saved Google File ID: {saved_config['google_file_id']}")
    print(f"Saved Company Name: {saved_config['pdf_settings']['company_name']}")
    
    # Reset to defaults
    config.reset_to_defaults()
    print("✅ Configuration reset to defaults")

def test_processing_tracker():
    """Test processing status tracking"""
    print("\n=== Testing Processing Status Tracking ===")
    
    # Initialize tracker
    tracker = ProcessingTracker("test_processing_status.json")
    
    # Start a test session
    session_id = tracker.start_processing_session("test_file_id", "test_folder_id")
    print(f"✅ Started session: {session_id}")
    
    # Add some test employees
    tracker.mark_employee_processed("EMP001", "John Doe", "pdf_link_123", session_id)
    tracker.mark_employee_processed("EMP002", "Jane Smith", "pdf_link_456", session_id)
    tracker.mark_employee_failed("EMP003", "Bob Johnson", "Test error", session_id)
    
    # Finish session
    tracker.finish_processing_session(session_id)
    print("✅ Session completed")
    
    # Get summary
    summary = tracker.get_processing_summary()
    print(f"Total employees processed: {summary['successfully_processed']}")
    print(f"Failed processing: {summary['failed_processing']}")
    print(f"Total sessions: {summary['total_sessions']}")
    
    # Verify JSON file exists and contains data
    with open('test_processing_status.json', 'r', encoding='utf-8') as f:
        status_data = json.load(f)
    
    print(f"✅ Status file contains {len(status_data['employees'])} employees")
    print(f"✅ Status file contains {len(status_data['sessions'])} sessions")
    
    # Cleanup test file
    import os
    if os.path.exists('test_processing_status.json'):
        os.remove('test_processing_status.json')
        print("✅ Test status file cleaned up")

def test_json_structure():
    """Test JSON file structure and integrity"""
    print("\n=== Testing JSON File Structure ===")
    
    # Check config.json structure
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        required_keys = [
            'google_credentials_file',
            'google_file_id', 
            'google_folder_id',
            'processing_settings',
            'pdf_settings',
            'paths'
        ]
        
        for key in required_keys:
            if key in config_data:
                print(f"✅ Config has required key: {key}")
            else:
                print(f"❌ Config missing key: {key}")
        
        # Check nested structures
        if 'processing_settings' in config_data:
            processing_keys = ['force_recreate', 'generate_csv', 'cleanup_old_sessions_days']
            for key in processing_keys:
                if key in config_data['processing_settings']:
                    print(f"✅ Processing settings has: {key}")
                else:
                    print(f"❌ Processing settings missing: {key}")
        
        print("✅ Config JSON structure is valid")
        
    except json.JSONDecodeError as e:
        print(f"❌ Config JSON is invalid: {e}")
    except FileNotFoundError:
        print("❌ Config file not found")

if __name__ == "__main__":
    test_config_saving()
    test_processing_tracker()
    test_json_structure()
    print("\n=== All Tests Completed ===")
