"""
Module for downloading files from Google Drive
Downloads Google Sheets as Excel files for local processing
"""

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import tempfile
import os
from typing import Tuple, Optional

class GoogleDriveDownloader:
    def __init__(self, credentials_file: str = None):
        """
        Initialize Google Drive downloader
        
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
            scopes = ['https://www.googleapis.com/auth/drive.readonly']
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            raise Exception(f"Authentication error: {e}")
    
    def get_file_info(self, file_id: str) -> dict:
        """
        Get file information from Google Drive
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File information
        """
        try:
            file_info = self.service.files().get(fileId=file_id).execute()
            return file_info
        except Exception as e:
            raise Exception(f"Error getting file info: {e}")
    
    def download_to_temp_file(self, file_id: str) -> Tuple[str, str]:
        """
        Download file from Google Drive to temporary file
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Tuple (temporary file path, original file name)
        """
        try:
            # Get file information
            file_info = self.get_file_info(file_id)
            original_name = file_info.get('name', 'unknown_file')
            mime_type = file_info.get('mimeType', '')
            
            print(f"📄 File: {original_name}")
            print(f"📋 MIME type: {mime_type}")
            
            # Determine download method
            if mime_type == 'application/vnd.google-apps.spreadsheet':
                # Google Sheets - export as Excel
                print("📊 Detected Google Sheets, exporting as Excel...")
                return self._download_google_sheets_as_excel(file_id, original_name)
            else:
                # Regular file - direct download
                print("📁 Detected regular file, downloading directly...")
                return self._download_regular_file(file_id, original_name)
                
        except Exception as e:
            raise Exception(f"Download error: {e}")
    
    def _download_google_sheets_as_excel(self, file_id: str, original_name: str) -> Tuple[str, str]:
        """
        Download Google Sheets as Excel file
        
        Args:
            file_id: Google Sheets file ID
            original_name: Original file name
            
        Returns:
            Tuple (temporary file path, original file name)
        """
        try:
            # Export as Excel
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            temp_path = temp_file.name
            
            # Download content
            content = request.execute()
            
            # Write to temporary file
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            print(f"✅ Google Sheets downloaded as Excel: {temp_path}")
            return temp_path, original_name
            
        except Exception as e:
            raise Exception(f"Error downloading Google Sheets: {e}")
    
    def _download_regular_file(self, file_id: str, original_name: str) -> Tuple[str, str]:
        """
        Download regular file
        
        Args:
            file_id: File ID
            original_name: Original file name
            
        Returns:
            Tuple (temporary file path, original file name)
        """
        try:
            # Get file content
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()
            
            # Determine file extension
            file_extension = os.path.splitext(original_name)[1] or '.bin'
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
            temp_path = temp_file.name
            
            # Write content
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            print(f"✅ File downloaded: {temp_path}")
            return temp_path, original_name
            
        except Exception as e:
            raise Exception(f"Error downloading file: {e}")
    
    def cleanup_temp_file(self, temp_path: str):
        """
        Delete temporary file
        
        Args:
            temp_path: Path to temporary file
        """
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"🗑️ Temporary file deleted: {temp_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not delete temporary file {temp_path}: {e}")

if __name__ == "__main__":
    # Testing
    from dotenv import load_dotenv
    load_dotenv()
    
    downloader = GoogleDriveDownloader()
    
    # Test file ID from .env
    test_file_id = os.getenv('GOOGLE_FILE_ID')
    
    if test_file_id:
        print(f"🧪 Testing download for file ID: {test_file_id}")
        try:
            temp_path, original_name = downloader.download_to_temp_file(test_file_id)
            print(f"✅ Download successful: {original_name} -> {temp_path}")
            
            # Check file size
            file_size = os.path.getsize(temp_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Clean up
            downloader.cleanup_temp_file(temp_path)
            
        except Exception as e:
            print(f"❌ Download error: {e}")
    else:
        print("❌ GOOGLE_FILE_ID not set in .env file")
