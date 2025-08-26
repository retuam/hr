"""
Full payroll processor:
1. Downloads file from Google Drive
2. Processes locally
3. Uploads PDF back to Google Drive
"""

import os
import tempfile
from typing import List, Dict, Any, Tuple
from datetime import datetime

from google_drive_downloader import GoogleDriveDownloader
from local_file_handler import LocalFileHandler
from pdf_generator import PayrollPDFGenerator
from google_drive_handler import GoogleDriveHandler
from processing_tracker import ProcessingTracker
from csv_generator import CSVGenerator
from config_manager import config

class FullPayrollProcessor:
    def __init__(self):
        """Initialize full payroll processor"""
        self.config = config
        self.downloader = GoogleDriveDownloader()
        self.file_handler = LocalFileHandler()
        self.pdf_generator = PayrollPDFGenerator()
        self.drive_handler = GoogleDriveHandler()
        self.tracker = ProcessingTracker(config.get_status_file_path())
        self.csv_generator = CSVGenerator()
        
        print("Full payroll processor initialized")
    
    def process_payrolls_full_cycle(self, google_file_id: str, google_folder_id: str, 
                                   sheet_name: str = None, force_recreate: bool = False,
                                   csv_folder_id: str = None) -> Dict[str, Any]:
        """
        Full cycle payroll processing
        
        Args:
            google_file_id: ID of Google Sheets/Drive file with employee data
            google_folder_id: ID of Google Drive folder to save PDFs
            sheet_name: Sheet name (for Excel files)
            force_recreate: Force recreation of already processed slips
            csv_folder_id: ID of Google Drive folder to save CSV reports (optional)
            
        Returns:
            Processing results
        """
        print(f"Starting full cycle payroll processing...")
        print(f"Google File ID: {google_file_id}")
        print(f"Google Folder ID: {google_folder_id}")
        print(f"📋 Sheet: {sheet_name or 'Default'}")
        print(f"🔄 Force recreation: {force_recreate}")
        
        # Start new processing session
        session_id = self.tracker.start_processing_session(google_file_id, google_folder_id)
        
        temp_file_path = None
        
        try:
            # Step 1: Download file from Google Drive
            print("\n📥 STEP 1: Downloading file from Google Drive...")
            temp_file_path, original_name = self.downloader.download_to_temp_file(google_file_id)
            print(f"✅ File downloaded: {original_name}")
            
            # Step 2: Validate file structure
            print("\n🔍 STEP 2: Validating file structure...")
            validation = self.file_handler.validate_file_structure(temp_file_path, sheet_name)
            
            if not validation['valid']:
                error_msg = f"File failed validation: {validation.get('error', 'Unknown error')}"
                if 'missing_required_columns' in validation:
                    error_msg += f"\nMissing required columns: {validation['missing_required_columns']}"
                raise ValueError(error_msg)
            
            print(f"✅ File is valid. Found data rows: {validation['rows_with_id']}")
            
            # Step 3: Load employee data
            print("\n👥 STEP 3: Loading employee data...")
            employees = self.file_handler.get_employee_data(temp_file_path, sheet_name)
            
            if not employees:
                raise ValueError("No employee data found in file")
            
            print(f"👥 Found employees: {len(employees)}")
            
            # Update total employees in session
            session_data = self.tracker.get_session_status(session_id)
            if session_data:
                session_data["total_employees"] = len(employees)
                session_data["source_file_name"] = original_name
                self.tracker._save_status_data()
            
            # Step 4: Process each employee
            print("\n⚙️ STEP 4: Processing employees...")
            
            results = {
                "session_id": session_id,
                "source_file_id": google_file_id,
                "source_file_name": original_name,
                "output_folder_id": google_folder_id,
                "total_employees": len(employees),
                "processed": [],
                "skipped": [],
                "failed": [],
                "processing_time": None
            }
            
            start_time = datetime.now()
            
            for i, employee in enumerate(employees, 1):
                employee_id = employee.get('id', '')
                employee_name = employee.get('name', 'Unknown')
                
                print(f"\n👤 Processing employee {i}/{len(employees)}: {employee_name} (ID: {employee_id})")
                
                try:
                    # Check if employee was already processed
                    if not force_recreate and self.tracker.is_employee_processed(employee_id):
                        print(f"⏭️ Employee {employee_name} already processed, skipping")
                        results["skipped"].append({
                            "employee_id": employee_id,
                            "employee_name": employee_name,
                            "reason": "already_processed"
                        })
                        continue
                    
                    # If force recreation, reset status
                    if force_recreate:
                        self.tracker.reset_employee_status(employee_id)
                    
                    # Process employee
                    drive_file_id, drive_link = self._process_single_employee_full_cycle(
                        employee, google_folder_id, session_id
                    )
                    
                    results["processed"].append({
                        "employee_id": employee_id,
                        "employee_name": employee_name,
                        "drive_file_id": drive_file_id,
                        "drive_link": drive_link
                    })
                    
                    print(f"✅ Employee {employee_name} processed successfully")
                    
                except Exception as e:
                    error_message = str(e)
                    print(f"❌ Error processing employee {employee_name}: {error_message}")
                    
                    # Mark as failed
                    self.tracker.mark_employee_failed(
                        employee_id, employee_name, error_message, session_id
                    )
                    
                    results["failed"].append({
                        "employee_id": employee_id,
                        "employee_name": employee_name,
                        "error": error_message
                    })
            
            # Finish session
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            results["processing_time"] = processing_time
            
            self.tracker.finish_processing_session(session_id)
            
            # Generate CSV report if folder specified
            if csv_folder_id:
                try:
                    print("\n📊 STEP 5: Generating CSV report...")
                    csv_file_id = self.csv_generator.generate_processing_report(results, csv_folder_id)
                    summary_csv_id = self.csv_generator.generate_summary_csv(results, csv_folder_id)
                    
                    results["csv_report_id"] = csv_file_id
                    results["csv_summary_id"] = summary_csv_id
                    print(f"✅ CSV reports generated and uploaded")
                    
                except Exception as e:
                    print(f"⚠️ Warning: CSV generation failed: {e}")
                    results["csv_error"] = str(e)
            
            # Print final statistics
            self._print_processing_summary(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Critical error during processing: {e}")
            # Mark session as failed
            session_data = self.tracker.get_session_status(session_id)
            if session_data:
                session_data["status"] = "failed"
                session_data["error"] = str(e)
                self.tracker._save_status_data()
            raise
        
        finally:
            # Clean up temporary file
            if temp_file_path:
                self.downloader.cleanup_temp_file(temp_file_path)
    
    def _process_single_employee_full_cycle(self, employee: Dict[str, Any], 
                                          google_folder_id: str, session_id: str) -> Tuple[str, str]:
        """
        Full processing of single employee: create PDF + upload to Drive
        
        Args:
            employee: Employee data
            google_folder_id: Google Drive folder ID
            session_id: Processing session ID
            
        Returns:
            Tuple (Drive file ID, file link)
        """
        employee_id = employee.get('id', '')
        employee_name = employee.get('name', 'Unknown')
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        
        try:
            # Generate PDF
            print(f"📄 Creating PDF for {employee_name}...")
            self.pdf_generator.generate_payroll_pdf(employee, temp_pdf_path)
            
            # Upload to Google Drive
            print(f"☁️ Uploading PDF to Google Drive...")
            drive_file_id = self.drive_handler.upload_payroll_pdf(
                temp_pdf_path, employee_id, employee_name, google_folder_id
            )
            
            # Get file link
            drive_link = self.drive_handler.get_file_link(drive_file_id)
            
            # Mark as processed
            self.tracker.mark_employee_processed(
                employee_id, employee_name, drive_file_id, session_id
            )
            
            return drive_file_id, drive_link
            
        finally:
            # Delete temporary PDF file
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
    
    def _print_processing_summary(self, results: Dict[str, Any]):
        """Print final processing statistics"""
        print("\n" + "="*60)
        print("📊 FULL CYCLE PROCESSING SUMMARY")
        print("="*60)
        print(f"📄 Source file: {results['source_file_name']} (ID: {results['source_file_id']})")
        print(f"📁 Google Drive folder: {results['output_folder_id']}")
        print(f"👥 Total employees: {results['total_employees']}")
        print(f"✅ Processed successfully: {len(results['processed'])}")
        print(f"⏭️ Skipped: {len(results['skipped'])}")
        print(f"❌ Errors: {len(results['failed'])}")
        
        if results['processing_time']:
            print(f"⏱️ Processing time: {results['processing_time']:.2f} seconds")
        
        success_rate = (len(results['processed']) / results['total_employees'] * 100) if results['total_employees'] > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        print(f"🆔 Session ID: {results['session_id']}")
        print("="*60)
        
        # Print links to created files
        if results['processed']:
            print("\n✅ CREATED PDF FILES IN GOOGLE DRIVE:")
            for processed in results['processed']:
                print(f"  • {processed['employee_name']} (ID: {processed['employee_id']})")
                print(f"    Link: {processed['drive_link']}")
        
        # Print error details
        if results['failed']:
            print("\n❌ ERROR DETAILS:")
            for failed in results['failed']:
                print(f"  • {failed['employee_name']} (ID: {failed['employee_id']}): {failed['error']}")
    
    def preview_source_file(self, google_file_id: str, sheet_name: str = None, rows: int = 5) -> Dict[str, Any]:
        """
        Preview source file from Google Drive
        
        Args:
            google_file_id: Google Drive file ID
            sheet_name: Sheet name
            rows: Number of rows to preview
            
        Returns:
            File information and preview
        """
        temp_file_path = None
        
        try:
            # Download file to temporary location
            temp_file_path, original_name = self.downloader.download_to_temp_file(google_file_id)
            
            # Validation
            validation = self.file_handler.validate_file_structure(temp_file_path, sheet_name)
            
            # Preview
            preview_df = self.file_handler.preview_file(temp_file_path, sheet_name, rows)
            
            # Get sheets (for Excel)
            sheets = self.file_handler.get_sheet_names(temp_file_path)
            
            return {
                "original_name": original_name,
                "validation": validation,
                "preview": preview_df.to_dict('records'),
                "columns": list(preview_df.columns),
                "sheets": sheets,
                "file_format": self.file_handler.detect_file_format(temp_file_path)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "validation": {"valid": False, "error": str(e)}
            }
        
        finally:
            # Clean up temporary file
            if temp_file_path:
                self.downloader.cleanup_temp_file(temp_file_path)
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get overall processing status
        
        Returns:
            Summary information about all processing
        """
        return self.tracker.get_processing_summary()
    
    def reset_employee(self, employee_id: str):
        """
        Reset specific employee status
        
        Args:
            employee_id: Employee ID
        """
        self.tracker.reset_employee_status(employee_id)
    
    def get_overall_status(self) -> Dict[str, Any]:
        """
        Get overall system status for Streamlit dashboard
        
        Returns:
            Dictionary with system status information
        """
        try:
            # Get basic tracker status using correct method
            status = self.tracker.get_processing_summary()
            
            return {
                'successfully_processed': status.get('successfully_processed', 0),
                'failed_processing': status.get('failed_processing', 0),
                'total_sessions': status.get('total_sessions', 0),
                'last_updated': status.get('last_updated', 'Never'),
                'recent_sessions': status.get('recent_sessions', []),
                'status_file': status.get('status_file', 'processing_status.json')
            }
        except Exception as e:
            print(f"Warning: Could not get status: {e}")
            return {
                'successfully_processed': 0,
                'failed_processing': 0,
                'total_sessions': 0,
                'last_updated': 'Unknown',
                'recent_sessions': [],
                'status_file': 'processing_status.json'
            }
    
    def process_payrolls_complete(self, google_file_id: str, google_folder_id: str, 
                                 sheet_name: str = None, force_recreate: bool = False,
                                 csv_folder_id: str = None) -> Dict[str, Any]:
        """
        Alias for process_payrolls_full_cycle for compatibility with Streamlit
        """
        return self.process_payrolls_full_cycle(google_file_id, google_folder_id, sheet_name, force_recreate, csv_folder_id)

if __name__ == "__main__":
    # Testing
    from dotenv import load_dotenv
    load_dotenv()
    
    processor = FullPayrollProcessor()
    
    # Get parameters from .env
    google_file_id = os.getenv('GOOGLE_FILE_ID')
    google_folder_id = os.getenv('GOOGLE_FOLDER')
    
    if google_file_id and google_folder_id:
        print("🧪 Running test preview...")
        try:
            preview = processor.preview_source_file(google_file_id)
            print(f"📋 Preview: {preview.get('original_name', 'Unknown')}")
            
            if preview.get('validation', {}).get('valid', False):
                print("✅ File passed validation")
                print(f"👥 Found employees: {preview['validation']['rows_with_id']}")
                
                # Can run full processing with CSV
                # results = processor.process_payrolls_full_cycle(
                #     google_file_id, 
                #     google_folder_id, 
                #     force_recreate=False,
                #     csv_folder_id=google_folder_id  # Use same folder for CSV
                # )
                # print("✅ Full processing completed successfully")
            else:
                print("❌ File failed validation")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
    else:
        print("❌ GOOGLE_FILE_ID and/or GOOGLE_FOLDER not set in .env file")
