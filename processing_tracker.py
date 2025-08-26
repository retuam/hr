"""
Module for tracking payroll processing status
Maintains JSON log of processed employees and sessions
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

class ProcessingTracker:
    def __init__(self, status_file: str = "processing_status.json"):
        """
        Initialize processing tracker
        
        Args:
            status_file: Path to JSON status file
        """
        self.status_file = status_file
        self.status_data = self._load_status_data()
        print(f"📊 Processing tracker initialized: {status_file}")
    
    def _load_status_data(self) -> Dict[str, Any]:
        """Load status data from JSON file"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"📂 Status data loaded: {len(data.get('employees', {}))} employees")
                return data
            else:
                print("📝 Creating new status file")
                return {
                    "employees": {},
                    "sessions": {},
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"⚠️ Error loading status data: {e}")
            return {
                "employees": {},
                "sessions": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_status_data(self):
        """Save status data to JSON file"""
        try:
            self.status_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error saving status data: {e}")
    
    def start_processing_session(self, source_file_id: str, output_folder_id: str) -> str:
        """
        Start new processing session
        
        Args:
            source_file_id: Source file ID
            output_folder_id: Output folder ID
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "source_file_id": source_file_id,
            "output_folder_id": output_folder_id,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "total_employees": 0,
            "processed_count": 0,
            "failed_count": 0,
            "source_file_name": None,
            "error": None
        }
        
        self.status_data["sessions"][session_id] = session_data
        self._save_status_data()
        
        print(f"🚀 Processing session started: {session_id}")
        return session_id
    
    def finish_processing_session(self, session_id: str):
        """
        Finish processing session
        
        Args:
            session_id: Session ID
        """
        if session_id in self.status_data["sessions"]:
            session_data = self.status_data["sessions"][session_id]
            session_data["status"] = "completed"
            session_data["finished_at"] = datetime.now().isoformat()
            
            self._save_status_data()
            print(f"✅ Processing session finished: {session_id}")
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session status
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None
        """
        return self.status_data["sessions"].get(session_id)
    
    def is_employee_processed(self, employee_id: str) -> bool:
        """
        Check if employee was already processed
        
        Args:
            employee_id: Employee ID
            
        Returns:
            True if processed, False otherwise
        """
        employee_data = self.status_data["employees"].get(employee_id, {})
        return employee_data.get("status") == "processed"
    
    def mark_employee_processed(self, employee_id: str, employee_name: str, 
                              drive_file_id: str, session_id: str):
        """
        Mark employee as processed
        
        Args:
            employee_id: Employee ID
            employee_name: Employee name
            drive_file_id: Google Drive file ID
            session_id: Processing session ID
        """
        employee_data = {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "status": "processed",
            "drive_file_id": drive_file_id,
            "processed_at": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        self.status_data["employees"][employee_id] = employee_data
        
        # Update session counters
        if session_id in self.status_data["sessions"]:
            self.status_data["sessions"][session_id]["processed_count"] += 1
        
        self._save_status_data()
        print(f"✅ Employee marked as processed: {employee_name} (ID: {employee_id})")
    
    def mark_employee_failed(self, employee_id: str, employee_name: str, 
                           error_message: str, session_id: str):
        """
        Mark employee processing as failed
        
        Args:
            employee_id: Employee ID
            employee_name: Employee name
            error_message: Error message
            session_id: Processing session ID
        """
        employee_data = {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "status": "failed",
            "error": error_message,
            "failed_at": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        self.status_data["employees"][employee_id] = employee_data
        
        # Update session counters
        if session_id in self.status_data["sessions"]:
            self.status_data["sessions"][session_id]["failed_count"] += 1
        
        self._save_status_data()
        print(f"❌ Employee marked as failed: {employee_name} (ID: {employee_id})")
    
    def reset_employee_status(self, employee_id: str):
        """
        Reset employee status (remove from processed)
        
        Args:
            employee_id: Employee ID
        """
        if employee_id in self.status_data["employees"]:
            del self.status_data["employees"][employee_id]
            self._save_status_data()
            print(f"🔄 Employee status reset: {employee_id}")
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get overall processing summary
        
        Returns:
            Summary statistics
        """
        employees = self.status_data["employees"]
        sessions = self.status_data["sessions"]
        
        processed_count = len([emp for emp in employees.values() if emp.get("status") == "processed"])
        failed_count = len([emp for emp in employees.values() if emp.get("status") == "failed"])
        
        recent_sessions = sorted(
            sessions.values(),
            key=lambda x: x.get("started_at", ""),
            reverse=True
        )[:5]  # Last 5 sessions
        
        return {
            "total_employees_ever_processed": len(employees),
            "successfully_processed": processed_count,
            "failed_processing": failed_count,
            "total_sessions": len(sessions),
            "recent_sessions": recent_sessions,
            "last_updated": self.status_data.get("last_updated"),
            "status_file": self.status_file
        }
    
    def get_employee_history(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing history for specific employee
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Employee processing history
        """
        return self.status_data["employees"].get(employee_id)
    
    def get_all_processed_employees(self) -> List[Dict[str, Any]]:
        """
        Get list of all processed employees
        
        Returns:
            List of processed employee data
        """
        return [
            emp for emp in self.status_data["employees"].values()
            if emp.get("status") == "processed"
        ]
    
    def cleanup_old_sessions(self, days: int = 30):
        """
        Remove sessions older than specified days
        
        Args:
            days: Number of days to keep
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions_to_remove = []
        
        for session_id, session_data in self.status_data["sessions"].items():
            started_at = session_data.get("started_at")
            if started_at:
                try:
                    session_date = datetime.fromisoformat(started_at)
                    if session_date < cutoff_date:
                        sessions_to_remove.append(session_id)
                except ValueError:
                    # Invalid date format, remove session
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.status_data["sessions"][session_id]
        
        if sessions_to_remove:
            self._save_status_data()
            print(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")

if __name__ == "__main__":
    # Testing
    tracker = ProcessingTracker("test_processing_status.json")
    
    # Test session
    session_id = tracker.start_processing_session("test_file_id", "test_folder_id")
    
    # Test employee processing
    tracker.mark_employee_processed("EMP001", "John Smith", "drive_file_123", session_id)
    tracker.mark_employee_failed("EMP002", "Jane Doe", "Test error", session_id)
    
    # Finish session
    tracker.finish_processing_session(session_id)
    
    # Get summary
    summary = tracker.get_processing_summary()
    print(f"📊 Summary: {summary}")
    
    # Check employee status
    print(f"EMP001 processed: {tracker.is_employee_processed('EMP001')}")
    print(f"EMP002 processed: {tracker.is_employee_processed('EMP002')}")
    
    # Clean up test file
    if os.path.exists("test_processing_status.json"):
        os.remove("test_processing_status.json")
        print("🗑️ Test file cleaned up")
