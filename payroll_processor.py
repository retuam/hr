"""
Final English Payroll Processor
Complete system for automated payroll processing from Google Sheets to PDF generation
"""

import os
import tempfile
from typing import List, Dict, Any, Tuple
from datetime import datetime

from english_google_drive_downloader import GoogleDriveDownloader
from english_local_file_handler import LocalFileHandler
from english_pdf_generator import PayrollPDFGenerator
from english_google_drive_handler import GoogleDriveHandler
from english_processing_tracker import ProcessingTracker

class FinalEnglishPayrollProcessor:
    def __init__(self):
        """Initialize the complete payroll processing system"""
        self.downloader = GoogleDriveDownloader()
        self.file_handler = LocalFileHandler()
        self.pdf_generator = PayrollPDFGenerator()
        self.drive_handler = GoogleDriveHandler()
        self.tracker = ProcessingTracker()
        
        print("🚀 Final English Payroll Processor initialized successfully")
    
    def process_payrolls_complete(self, google_file_id: str, google_folder_id: str, 
                                 sheet_name: str = None, force_recreate: bool = False) -> Dict[str, Any]:
        """
        Complete payroll processing cycle
        
        Args:
            google_file_id: ID of Google Sheets/Drive file with employee data
            google_folder_id: ID of Google Drive folder to save PDFs
            sheet_name: Sheet name (for Excel files)
            force_recreate: Force recreation of already processed payroll slips
            
        Returns:
            Complete processing results
        """
        print(f"🔄 Starting complete payroll processing cycle...")
        print(f"📄 Google File ID: {google_file_id}")
        print(f"📁 Google Folder ID: {google_folder_id}")
        print(f"📋 Sheet: {sheet_name or 'Default'}")
        print(f"🔄 Force recreation: {force_recreate}")
        
        # Start new processing session
        session_id = self.tracker.start_processing_session(google_file_id, google_folder_id)
        
        temp_file_path = None
        
        try:
            # Step 1: Download file from Google Drive
            print("\n📥 STEP 1: Downloading file from Google Drive...")
            temp_file_path, original_name = self.downloader.download_to_temp_file(google_file_id)
            print(f"✅ File downloaded successfully: {original_name}")
            
            # Step 2: Validate file structure
            print("\n🔍 STEP 2: Validating file structure...")
            validation = self.file_handler.validate_file_structure(temp_file_path, sheet_name)
            
            if not validation['valid']:
                error_msg = f"File validation failed: {validation.get('error', 'Unknown error')}"
                if 'missing_required_columns' in validation:
                    error_msg += f"\nMissing required columns: {validation['missing_required_columns']}"
                raise ValueError(error_msg)
            
            print(f"✅ File validation passed. Found {validation['rows_with_id']} valid employee records")
            
            # Step 3: Load employee data
            print("\n👥 STEP 3: Loading employee data...")
            employees = self.file_handler.get_employee_data(temp_file_path, sheet_name)
            
            if not employees:
                raise ValueError("No employee data found in the file")
            
            print(f"👥 Successfully loaded {len(employees)} employee records")
            
            # Update session information
            session_data = self.tracker.get_session_status(session_id)
            if session_data:
                session_data["total_employees"] = len(employees)
                session_data["source_file_name"] = original_name
                self.tracker._save_status_data()
            
            # Step 4: Process each employee
            print("\n⚙️ STEP 4: Processing individual employee payroll slips...")
            
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
                employee_name = employee.get('name', 'Unknown Employee')
                
                print(f"\n👤 Processing employee {i}/{len(employees)}: {employee_name} (ID: {employee_id})")
                
                try:
                    # Check if employee was already processed
                    if not force_recreate and self.tracker.is_employee_processed(employee_id):
                        print(f"⏭️ Employee {employee_name} already processed, skipping...")
                        results["skipped"].append({
                            "employee_id": employee_id,
                            "employee_name": employee_name,
                            "reason": "already_processed"
                        })
                        continue
                    
                    # If force recreation, reset status
                    if force_recreate:
                        self.tracker.reset_employee_status(employee_id)
                    
                    # Process individual employee
                    drive_file_id, drive_link = self._process_individual_employee(
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
                    
                    # Mark as failed in tracker
                    self.tracker.mark_employee_failed(
                        employee_id, employee_name, error_message, session_id
                    )
                    
                    results["failed"].append({
                        "employee_id": employee_id,
                        "employee_name": employee_name,
                        "error": error_message
                    })
            
            # Calculate processing time and finish session
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            results["processing_time"] = processing_time
            
            self.tracker.finish_processing_session(session_id)
            
            # Print comprehensive summary
            self._print_comprehensive_summary(results)
            
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
    
    def _process_individual_employee(self, employee: Dict[str, Any], 
                                   google_folder_id: str, session_id: str) -> Tuple[str, str]:
        """
        Process individual employee: create PDF and upload to Drive
        
        Args:
            employee: Employee data dictionary
            google_folder_id: Google Drive folder ID for uploads
            session_id: Current processing session ID
            
        Returns:
            Tuple of (Drive file ID, shareable link)
        """
        employee_id = employee.get('id', '')
        employee_name = employee.get('name', 'Unknown Employee')
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        
        try:
            # Generate PDF payroll slip
            print(f"📄 Generating PDF payroll slip for {employee_name}...")
            self.pdf_generator.generate_payroll_pdf(employee, temp_pdf_path)
            
            # Upload to Google Drive
            print(f"☁️ Uploading PDF to Google Drive...")
            drive_file_id = self.drive_handler.upload_payroll_pdf(
                temp_pdf_path, employee_id, employee_name, google_folder_id
            )
            
            # Get shareable link
            drive_link = self.drive_handler.get_file_link(drive_file_id)
            
            # Mark as successfully processed
            self.tracker.mark_employee_processed(
                employee_id, employee_name, drive_file_id, session_id
            )
            
            return drive_file_id, drive_link
            
        finally:
            # Always clean up temporary PDF file
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
    
    def _print_comprehensive_summary(self, results: Dict[str, Any]):
        """Print comprehensive processing summary"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE PAYROLL PROCESSING SUMMARY")
        print("="*70)
        print(f"📄 Source file: {results['source_file_name']} (ID: {results['source_file_id']})")
        print(f"📁 Output Google Drive folder: {results['output_folder_id']}")
        print(f"👥 Total employees in file: {results['total_employees']}")
        print(f"✅ Successfully processed: {len(results['processed'])}")
        print(f"⏭️ Skipped (already processed): {len(results['skipped'])}")
        print(f"❌ Failed with errors: {len(results['failed'])}")
        
        if results['processing_time']:
            print(f"⏱️ Total processing time: {results['processing_time']:.2f} seconds")
            avg_time = results['processing_time'] / results['total_employees'] if results['total_employees'] > 0 else 0
            print(f"⏱️ Average time per employee: {avg_time:.2f} seconds")
        
        success_rate = (len(results['processed']) / results['total_employees'] * 100) if results['total_employees'] > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        print(f"🆔 Session ID: {results['session_id']}")
        print("="*70)
        
        # Print links to successfully created files
        if results['processed']:
            print("\n✅ SUCCESSFULLY CREATED PAYROLL SLIPS:")
            for processed in results['processed']:
                print(f"  • {processed['employee_name']} (ID: {processed['employee_id']})")
                print(f"    📎 Google Drive Link: {processed['drive_link']}")
        
        # Print skipped employees
        if results['skipped']:
            print("\n⏭️ SKIPPED EMPLOYEES (ALREADY PROCESSED):")
            for skipped in results['skipped']:
                print(f"  • {skipped['employee_name']} (ID: {skipped['employee_id']})")
        
        # Print detailed error information
        if results['failed']:
            print("\n❌ FAILED PROCESSING - DETAILED ERROR INFORMATION:")
            for failed in results['failed']:
                print(f"  • {failed['employee_name']} (ID: {failed['employee_id']})")
                print(f"    Error: {failed['error']}")
    
    def preview_source_file(self, google_file_id: str, sheet_name: str = None, rows: int = 5) -> Dict[str, Any]:
        """
        Preview source file from Google Drive
        
        Args:
            google_file_id: Google Drive file ID
            sheet_name: Sheet name for Excel files
            rows: Number of rows to preview
            
        Returns:
            File information and preview data
        """
        temp_file_path = None
        
        try:
            # Download file to temporary location
            temp_file_path, original_name = self.downloader.download_to_temp_file(google_file_id)
            
            # Validate file structure
            validation = self.file_handler.validate_file_structure(temp_file_path, sheet_name)
            
            # Get preview data
            preview_df = self.file_handler.preview_file(temp_file_path, sheet_name, rows)
            
            # Get available sheets (for Excel files)
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
    
    def get_overall_status(self) -> Dict[str, Any]:
        """
        Get overall processing status and statistics
        
        Returns:
            Comprehensive status information
        """
        return self.tracker.get_processing_summary()
    
    def reset_employee_status(self, employee_id: str):
        """
        Reset processing status for specific employee
        
        Args:
            employee_id: Employee ID to reset
        """
        self.tracker.reset_employee_status(employee_id)

if __name__ == "__main__":
    # Testing and demonstration
    from dotenv import load_dotenv
    load_dotenv()
    
    processor = FinalEnglishPayrollProcessor()
    
    # Get configuration from environment variables
    google_file_id = os.getenv('GOOGLE_FILE_ID')
    google_folder_id = os.getenv('GOOGLE_FOLDER')
    
    if google_file_id and google_folder_id:
        print("🧪 Running demonstration with real configuration...")
        try:
            # Preview the source file
            preview = processor.preview_source_file(google_file_id)
            print(f"📋 Source file preview: {preview.get('original_name', 'Unknown')}")
            
            if preview.get('validation', {}).get('valid', False):
                print("✅ Source file passed validation")
                print(f"👥 Found {preview['validation']['rows_with_id']} valid employee records")
                
                # Uncomment to run full processing
                # print("\n🚀 Starting full processing cycle...")
                # results = processor.process_payrolls_complete(
                #     google_file_id, 
                #     google_folder_id, 
                #     force_recreate=False
                # )
                # print("✅ Complete processing cycle finished successfully")
            else:
                print("❌ Source file failed validation")
                print(f"Error: {preview.get('validation', {}).get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during demonstration: {e}")
    else:
        print("❌ GOOGLE_FILE_ID and/or GOOGLE_FOLDER not configured in .env file")
        print("Please set these environment variables to test the system")
