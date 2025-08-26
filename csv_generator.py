"""
Module for generating CSV reports with PDF links and employee IDs
Creates CSV files with processing results for easy tracking
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from google_drive_handler import GoogleDriveHandler

class CSVGenerator:
    def __init__(self):
        """Initialize CSV generator"""
        print("📊 CSV generator initialized")
    
    def generate_processing_report(self, results: Dict[str, Any], csv_folder_id: str) -> str:
        """
        Generate CSV report with processing results and upload to Google Drive
        
        Args:
            results: Processing results from payroll processor
            csv_folder_id: Google Drive folder ID for CSV upload
            
        Returns:
            Google Drive file ID of uploaded CSV
        """
        try:
            # Create temporary CSV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"payroll_processing_report_{timestamp}.csv"
            temp_csv_path = os.path.join(os.getcwd(), csv_filename)
            
            # Prepare CSV data
            csv_data = []
            
            # Add header
            csv_data.append([
                "Employee ID",
                "Employee Name", 
                "Status",
                "PDF Link",
                "Processing Date",
                "Session ID",
                "Error Message"
            ])
            
            # Add processed employees
            for processed in results.get('processed', []):
                csv_data.append([
                    processed.get('employee_id', ''),
                    processed.get('employee_name', ''),
                    'Processed',
                    processed.get('drive_link', ''),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    results.get('session_id', ''),
                    ''
                ])
            
            # Add skipped employees
            for skipped in results.get('skipped', []):
                csv_data.append([
                    skipped.get('employee_id', ''),
                    skipped.get('employee_name', ''),
                    'Skipped',
                    '',
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    results.get('session_id', ''),
                    skipped.get('reason', 'Already processed')
                ])
            
            # Add failed employees
            for failed in results.get('failed', []):
                csv_data.append([
                    failed.get('employee_id', ''),
                    failed.get('employee_name', ''),
                    'Failed',
                    '',
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    results.get('session_id', ''),
                    failed.get('error', '')
                ])
            
            # Write CSV file
            with open(temp_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_data)
            
            print(f"📊 CSV report created: {csv_filename}")
            print(f"   Total records: {len(csv_data) - 1}")  # -1 for header
            
            # Upload to Google Drive
            drive_handler = GoogleDriveHandler()
            csv_file_id = drive_handler.upload_csv_report(
                temp_csv_path, csv_filename, csv_folder_id
            )
            
            # Clean up temporary file
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
                print(f"🗑️ Temporary CSV file cleaned up: {temp_csv_path}")
            
            return csv_file_id
            
        except Exception as e:
            # Clean up temporary file on error
            if 'temp_csv_path' in locals() and os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
            raise Exception(f"Error generating CSV report: {e}")
    
    def generate_summary_csv(self, results: Dict[str, Any], csv_folder_id: str) -> str:
        """
        Generate summary CSV with key statistics
        
        Args:
            results: Processing results
            csv_folder_id: Google Drive folder ID for CSV upload
            
        Returns:
            Google Drive file ID of uploaded CSV
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"payroll_summary_{timestamp}.csv"
            temp_csv_path = os.path.join(os.getcwd(), csv_filename)
            
            # Summary data
            summary_data = [
                ["Metric", "Value"],
                ["Processing Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Session ID", results.get('session_id', '')],
                ["Source File", results.get('source_file_name', '')],
                ["Total Employees", results.get('total_employees', 0)],
                ["Successfully Processed", len(results.get('processed', []))],
                ["Skipped", len(results.get('skipped', []))],
                ["Failed", len(results.get('failed', []))],
                ["Processing Time (seconds)", results.get('processing_time', 0)],
                ["Success Rate (%)", f"{(len(results.get('processed', [])) / max(results.get('total_employees', 1), 1) * 100):.1f}"]
            ]
            
            # Write summary CSV
            with open(temp_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(summary_data)
            
            print(f"📈 Summary CSV created: {csv_filename}")
            
            # Upload to Google Drive
            drive_handler = GoogleDriveHandler()
            csv_file_id = drive_handler.upload_csv_report(
                temp_csv_path, csv_filename, csv_folder_id
            )
            
            # Clean up
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
            
            return csv_file_id
            
        except Exception as e:
            if 'temp_csv_path' in locals() and os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
            raise Exception(f"Error generating summary CSV: {e}")

if __name__ == "__main__":
    # Testing
    generator = CSVGenerator()
    
    # Test data
    test_results = {
        'session_id': 'test_session_123',
        'source_file_name': 'test_payroll.xlsx',
        'total_employees': 3,
        'processed': [
            {
                'employee_id': '001',
                'employee_name': 'Test Employee 1',
                'drive_link': 'https://drive.google.com/file/d/test1/view'
            }
        ],
        'skipped': [
            {
                'employee_id': '002', 
                'employee_name': 'Test Employee 2',
                'reason': 'already_processed'
            }
        ],
        'failed': [
            {
                'employee_id': '003',
                'employee_name': 'Test Employee 3', 
                'error': 'Test error'
            }
        ],
        'processing_time': 45.5
    }
    
    print("🧪 Testing CSV generation...")
    
    # Create test CSV locally (without Google Drive upload)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_csv = f"test_report_{timestamp}.csv"
    
    try:
        csv_data = []
        csv_data.append([
            "Employee ID", "Employee Name", "Status", "PDF Link", 
            "Processing Date", "Session ID", "Error Message"
        ])
        
        for processed in test_results.get('processed', []):
            csv_data.append([
                processed.get('employee_id', ''),
                processed.get('employee_name', ''),
                'Processed',
                processed.get('drive_link', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                test_results.get('session_id', ''),
                ''
            ])
        
        with open(test_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
        
        print(f"✅ Test CSV created: {test_csv}")
        print(f"📊 Records: {len(csv_data) - 1}")
        
        # Clean up test file
        if os.path.exists(test_csv):
            os.unlink(test_csv)
            print(f"🗑️ Test file cleaned up")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
