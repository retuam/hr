"""
Module for handling Google Drive operations
Uploads files, creates folders, manages permissions
"""

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
import os
from datetime import datetime
from typing import Optional

class GoogleDriveHandler:
    def __init__(self, credentials_file: str = None):
        """
        Initialize Google Drive handler
        
        Args:
            credentials_file: Path to service account JSON file
        """
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE')
        if not self.credentials_file:
            raise ValueError("Google credentials file not specified")
        
        self.service = self._authenticate()
        print("🔑 Google Drive API authenticated successfully")
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            scopes = ['https://www.googleapis.com/auth/drive']
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            raise Exception(f"Authentication error: {e}")
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Create folder in Google Drive
        
        Args:
            folder_name: Name of folder to create
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            Created folder ID
        """
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(body=folder_metadata).execute()
            folder_id = folder.get('id')
            
            print(f"📁 Folder created: {folder_name} (ID: {folder_id})")
            return folder_id
            
        except Exception as e:
            raise Exception(f"Error creating folder: {e}")
    
    def folder_exists(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """
        Check if folder exists
        
        Args:
            folder_name: Name of folder to check
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            Folder ID if exists, None otherwise
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                return items[0]['id']
            return None
            
        except Exception as e:
            print(f"⚠️ Error checking folder existence: {e}")
            return None
    
    def get_or_create_date_folder(self, parent_folder_id: str) -> str:
        """
        Get or create date-based folder (YYYY-MM format)
        
        Args:
            parent_folder_id: ID of parent folder
            
        Returns:
            Date folder ID
        """
        try:
            # Current date in YYYY-MM format
            current_date = datetime.now().strftime("%Y-%m")
            
            # Check if folder exists
            folder_id = self.folder_exists(current_date, parent_folder_id)
            
            if folder_id:
                print(f"📅 Date folder found: {current_date} (ID: {folder_id})")
                return folder_id
            else:
                # Create new folder
                folder_id = self.create_folder(current_date, parent_folder_id)
                print(f"📅 Date folder created: {current_date} (ID: {folder_id})")
                return folder_id
                
        except Exception as e:
            raise Exception(f"Error getting/creating date folder: {e}")
    
    def upload_file(self, file_path: str, file_name: str, parent_folder_id: str = None) -> str:
        """
        Upload file to Google Drive
        
        Args:
            file_path: Local path to file
            file_name: Name for file in Drive
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            Uploaded file ID
        """
        try:
            file_metadata = {'name': file_name}
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            print(f"☁️ File uploaded: {file_name} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            raise Exception(f"Error uploading file: {e}")
    
    def upload_payroll_pdf(self, pdf_path: str, employee_id: str, 
                          employee_name: str, parent_folder_id: str) -> str:
        """
        Upload payroll PDF with proper naming and folder structure
        
        Args:
            pdf_path: Local path to PDF file
            employee_id: Employee ID
            employee_name: Employee name
            parent_folder_id: ID of parent folder
            
        Returns:
            Uploaded file ID
        """
        try:
            # Get or create date folder
            date_folder_id = self.get_or_create_date_folder(parent_folder_id)
            
            # Generate file name
            current_date = datetime.now().strftime("%Y-%m")
            safe_name = "".join(c for c in employee_name if c.isalnum() or c in (' ', '-', '_')).strip()
            file_name = f"Payroll_{current_date}_{employee_id}_{safe_name}.pdf"
            
            # Upload file
            file_id = self.upload_file(pdf_path, file_name, date_folder_id)
            
            print(f"📄 Payroll PDF uploaded: {file_name}")
            return file_id
            
        except Exception as e:
            raise Exception(f"Error uploading payroll PDF: {e}")
    
    def get_file_link(self, file_id: str) -> str:
        """
        Get shareable link for file
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Shareable link
        """
        try:
            # Make file accessible to anyone with link
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            # Get file info
            file_info = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            link = file_info.get('webViewLink', f'https://drive.google.com/file/d/{file_id}/view')
            return link
            
        except Exception as e:
            print(f"⚠️ Error getting file link: {e}")
            return f'https://drive.google.com/file/d/{file_id}/view'
    
    def upload_csv_report(self, csv_path: str, csv_filename: str, parent_folder_id: str) -> str:
        """
        Upload CSV report to Google Drive
        
        Args:
            csv_path: Local path to CSV file
            csv_filename: Name for CSV file in Drive
            parent_folder_id: ID of parent folder
            
        Returns:
            Uploaded CSV file ID
        """
        try:
            # Get or create date folder
            date_folder_id = self.get_or_create_date_folder(parent_folder_id)
            
            # Upload CSV file
            file_id = self.upload_file(csv_path, csv_filename, date_folder_id)
            
            print(f"📊 CSV report uploaded: {csv_filename}")
            return file_id
            
        except Exception as e:
            raise Exception(f"Error uploading CSV report: {e}")
    
    def get_folder_info(self, folder_id: str) -> dict:
        """
        Get folder information
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            Folder information
        """
        try:
            folder_info = self.service.files().get(
                fileId=folder_id,
                fields='id,name,parents,createdTime,modifiedTime'
            ).execute()
            
            return folder_info
            
        except Exception as e:
            raise Exception(f"Error getting folder info: {e}")

if __name__ == "__main__":
    # Testing
    from dotenv import load_dotenv
    load_dotenv()
    
    handler = GoogleDriveHandler()
    
    # Test folder ID from .env
    test_folder_id = os.getenv('GOOGLE_FOLDER')
    
    if test_folder_id:
        print(f"🧪 Testing with folder ID: {test_folder_id}")
        
        try:
            # Get folder info
            folder_info = handler.get_folder_info(test_folder_id)
            print(f"📁 Folder: {folder_info.get('name', 'Unknown')}")
            
            # Test date folder creation
            date_folder_id = handler.get_or_create_date_folder(test_folder_id)
            print(f"📅 Date folder ID: {date_folder_id}")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
    else:
        print("❌ GOOGLE_FOLDER not set in .env file")
