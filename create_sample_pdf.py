"""
Create a sample PDF payroll slip for testing
"""

import os
from dotenv import load_dotenv
from google_drive_downloader import GoogleDriveDownloader
from local_file_handler import LocalFileHandler
from pdf_generator import PayrollPDFGenerator

def create_sample_pdf():
    """Create a sample PDF from real data"""
    print("📄 Creating sample PDF payroll slip...")
    
    # Load environment
    load_dotenv()
    
    google_file_id = os.getenv('GOOGLE_FILE_ID')
    if not google_file_id:
        print("❌ GOOGLE_FILE_ID not set")
        return
    
    temp_file_path = None
    
    try:
        # Download and parse data
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        if credentials_file and not os.path.isabs(credentials_file):
            credentials_file = os.path.join(os.getcwd(), credentials_file)
        
        downloader = GoogleDriveDownloader(credentials_file)
        temp_file_path, original_name = downloader.download_to_temp_file(google_file_id)
        
        file_handler = LocalFileHandler()
        employees = file_handler.get_employee_data(temp_file_path)
        
        if not employees:
            print("❌ No employee data found")
            return
        
        # Get first employee
        employee = employees[0]
        employee_name = employee.get('name', 'Unknown')
        employee_id = employee.get('id', 'Unknown')
        
        print(f"👤 Creating PDF for: {employee_name} (ID: {employee_id})")
        
        # Generate PDF with timestamp to avoid conflicts
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in employee_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        output_file = f"sample_payroll_{employee_id}_{safe_name}_{timestamp}.pdf"
        
        pdf_generator = PayrollPDFGenerator()
        pdf_generator.generate_payroll_pdf(employee, output_file)
        
        print(f"✅ PDF created: {output_file}")
        print(f"📊 File size: {os.path.getsize(output_file)} bytes")
        
        # Show ALL employee data for debugging
        print(f"\n👤 Employee Data:")
        for key, value in employee.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 Key Values:")
        print(f"   Name: {employee.get('name', 'N/A')}")
        print(f"   ID: {employee.get('id', 'N/A')}")
        print(f"   Location: {employee.get('location', 'N/A')}")
        print(f"   Base: ${employee.get('base', 0):.2f}")
        print(f"   Bonus USD: ${employee.get('bonus_usd', 0):.2f}")
        print(f"   SLA: {employee.get('sla', 0):.1f}%")
        print(f"   Percent from base: {employee.get('percent_from_base', 0):.3f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if temp_file_path:
            downloader.cleanup_temp_file(temp_file_path)

if __name__ == "__main__":
    create_sample_pdf()
