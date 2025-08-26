"""
Test main flow: Download -> Parse -> Generate PDF
Tests the complete payroll processing workflow
"""

import os
import tempfile
from dotenv import load_dotenv

# Import our modules
from google_drive_downloader import GoogleDriveDownloader
from local_file_handler import LocalFileHandler
from pdf_generator import PayrollPDFGenerator

def test_main_flow():
    """Test the complete workflow: download -> parse -> generate PDF"""
    print("🧪 Testing Main Payroll Processing Flow")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    google_file_id = os.getenv('GOOGLE_FILE_ID')
    
    if not google_file_id:
        print("❌ GOOGLE_FILE_ID not set in .env file")
        return False
    
    temp_file_path = None
    
    try:
        # Step 1: Download file from Google Drive
        print("\n📥 STEP 1: Testing Google Drive Download")
        print("-" * 30)
        
        # Check credentials file
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        if credentials_file and not os.path.isabs(credentials_file):
            credentials_file = os.path.join(os.getcwd(), credentials_file)
        
        if not credentials_file or not os.path.exists(credentials_file):
            print(f"❌ Google credentials file not found: {credentials_file}")
            return False
        
        downloader = GoogleDriveDownloader(credentials_file)
        temp_file_path, original_name = downloader.download_to_temp_file(google_file_id)
        
        print(f"✅ Download successful!")
        print(f"   Original name: {original_name}")
        print(f"   Temp file: {temp_file_path}")
        print(f"   File size: {os.path.getsize(temp_file_path)} bytes")
        
        # Step 2: Parse and validate file
        print("\n🔍 STEP 2: Testing File Parsing and Validation")
        print("-" * 30)
        
        file_handler = LocalFileHandler()
        
        # Validate structure
        validation = file_handler.validate_file_structure(temp_file_path)
        
        if not validation['valid']:
            print(f"❌ File validation failed: {validation['error']}")
            return False
        
        print(f"✅ File validation passed!")
        print(f"   Total rows: {validation['total_rows']}")
        print(f"   Valid employee records: {validation['rows_with_id']}")
        print(f"   Columns: {validation['columns']}")
        
        # Get employee data
        employees = file_handler.get_employee_data(temp_file_path)
        
        if not employees:
            print("❌ No employee data found")
            return False
        
        print(f"✅ Employee data extracted!")
        print(f"   Found {len(employees)} employees")
        
        # Show first employee as example
        if employees:
            first_employee = employees[0]
            print(f"   Example employee: {first_employee.get('name', 'Unknown')} (ID: {first_employee.get('id', 'Unknown')})")
        
        # Step 3: Generate PDF for first employee
        print("\n📄 STEP 3: Testing PDF Generation")
        print("-" * 30)
        
        pdf_generator = PayrollPDFGenerator()
        
        # Use first employee for testing
        test_employee = employees[0]
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            test_pdf_path = temp_pdf.name
        
        try:
            # Generate PDF
            pdf_generator.generate_payroll_pdf(test_employee, test_pdf_path)
            
            print(f"✅ PDF generation successful!")
            print(f"   Employee: {test_employee.get('name', 'Unknown')}")
            print(f"   PDF file: {test_pdf_path}")
            print(f"   PDF size: {os.path.getsize(test_pdf_path)} bytes")
            
            # Verify PDF was created and has content
            if os.path.exists(test_pdf_path) and os.path.getsize(test_pdf_path) > 1000:
                print("✅ PDF file created successfully with content")
            else:
                print("❌ PDF file is empty or too small")
                return False
            
        finally:
            # Clean up test PDF
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)
                print(f"🗑️ Test PDF cleaned up: {test_pdf_path}")
        
        # Step 4: Test with multiple employees (first 3)
        print("\n👥 STEP 4: Testing Multiple Employee Processing")
        print("-" * 30)
        
        test_count = min(3, len(employees))
        successful_pdfs = 0
        
        for i in range(test_count):
            employee = employees[i]
            employee_name = employee.get('name', f'Employee_{i+1}')
            
            print(f"   Processing {i+1}/{test_count}: {employee_name}")
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                test_pdf_path = temp_pdf.name
            
            try:
                pdf_generator.generate_payroll_pdf(employee, test_pdf_path)
                
                if os.path.exists(test_pdf_path) and os.path.getsize(test_pdf_path) > 1000:
                    successful_pdfs += 1
                    print(f"   ✅ {employee_name}: PDF created successfully")
                else:
                    print(f"   ❌ {employee_name}: PDF creation failed")
                
            except Exception as e:
                print(f"   ❌ {employee_name}: Error - {e}")
            
            finally:
                if os.path.exists(test_pdf_path):
                    os.unlink(test_pdf_path)
        
        print(f"\n📊 Multiple processing results: {successful_pdfs}/{test_count} successful")
        
        # Final summary
        print("\n🎉 MAIN FLOW TEST SUMMARY")
        print("="*50)
        print("✅ Google Drive download: PASSED")
        print("✅ File validation: PASSED")
        print("✅ Employee data extraction: PASSED")
        print("✅ PDF generation: PASSED")
        print(f"✅ Multiple employee processing: {successful_pdfs}/{test_count} PASSED")
        
        if successful_pdfs == test_count:
            print("\n🎊 ALL TESTS PASSED! Main flow is working correctly.")
            return True
        else:
            print(f"\n⚠️ Some tests failed. Success rate: {successful_pdfs}/{test_count}")
            return False
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            downloader.cleanup_temp_file(temp_file_path)

def test_individual_components():
    """Test individual components separately"""
    print("\n🔧 INDIVIDUAL COMPONENT TESTS")
    print("="*50)
    
    # Load environment variables first
    load_dotenv()
    
    # Check credentials file exists
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    if credentials_file and not os.path.isabs(credentials_file):
        credentials_file = os.path.join(os.getcwd(), credentials_file)
    
    print(f"📋 Checking configuration:")
    print(f"   Credentials file: {credentials_file}")
    print(f"   File exists: {os.path.exists(credentials_file) if credentials_file else False}")
    print(f"   Google File ID: {os.getenv('GOOGLE_FILE_ID', 'Not set')}")
    print(f"   Google Folder ID: {os.getenv('GOOGLE_FOLDER', 'Not set')}")
    
    if not credentials_file or not os.path.exists(credentials_file):
        print(f"❌ Google credentials file not found: {credentials_file}")
        return False
    
    # Test 1: Google Drive Downloader
    print("\n1. Testing Google Drive Downloader...")
    try:
        downloader = GoogleDriveDownloader(credentials_file)
        print("✅ Google Drive Downloader initialized successfully")
    except Exception as e:
        print(f"❌ Google Drive Downloader failed: {e}")
        return False
    
    # Test 2: Local File Handler
    print("\n2. Testing Local File Handler...")
    try:
        file_handler = LocalFileHandler()
        print("✅ Local File Handler initialized successfully")
    except Exception as e:
        print(f"❌ Local File Handler failed: {e}")
        return False
    
    # Test 3: PDF Generator
    print("\n3. Testing PDF Generator...")
    try:
        pdf_generator = PayrollPDFGenerator()
        print("✅ PDF Generator initialized successfully")
    except Exception as e:
        print(f"❌ PDF Generator failed: {e}")
        return False
    
    print("\n✅ All individual components initialized successfully!")
    return True

def main():
    """Main test function"""
    print("🚀 Starting Payroll Processing System Tests")
    print("="*60)
    
    # Test individual components first
    if not test_individual_components():
        print("\n❌ Individual component tests failed. Stopping.")
        return
    
    # Test main flow
    if test_main_flow():
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The payroll processing system is ready for production use.")
    else:
        print("\n❌ MAIN FLOW TESTS FAILED!")
        print("Please check the configuration and try again.")

if __name__ == "__main__":
    main()
