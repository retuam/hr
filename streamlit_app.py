"""
Final English Streamlit Application for Payroll Processing
Complete web interface for automated payroll slip generation
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our payroll processor and config
from full_payroll_processor import FullPayrollProcessor
from config_manager import config

# Page configuration
st.set_page_config(
    page_title="Payroll Processing System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def authenticate():
    """Simple authentication system"""
    # Initialize authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("Payroll System Authentication")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                admin_username = os.getenv('ADMIN_USERNAME')
                admin_password = os.getenv('ADMIN_PASSWORD')
                
                if username == admin_username and password == admin_password:
                    st.session_state.authenticated = True
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.info("Use admin credentials from .env file")
        return False
    
    return True

def main():
    """Main application"""
    if not authenticate():
        return
    
    # Initialize processor
    if "processor" not in st.session_state:
        try:
            st.session_state.processor = FullPayrollProcessor()
        except Exception as e:
            st.error(f"Error initializing processor: {e}")
            st.stop()
    
    # Sidebar navigation
    st.sidebar.title("Payroll System")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Select Page",
        ["Home", "File Preview", "Process Payrolls", "Statistics", "Settings"]
    )
    
    # Route to selected page
    if page == "Home":
        show_home_page()
    elif page == "File Preview":
        show_preview_page()
    elif page == "Process Payrolls":
        show_processing_page()
    elif page == "Statistics":
        show_statistics_page()
    elif page == "Settings":
        show_settings_page()

def show_home_page():
    """Home page with system overview"""
    st.title("Payroll Processing System")
    st.markdown("### Welcome to the Automated Payroll Slip Generation System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### System Features
        - **Google Drive Integration**: Download payroll data from Google Sheets
        - **PDF Generation**: Create professional payroll slips
        - **Cloud Upload**: Automatically upload PDFs to Google Drive
        - **Progress Tracking**: Monitor processing status and history
        - **Smart Processing**: Avoid duplicate processing
        """)
    
    with col2:
        st.markdown("""
        #### Quick Start
        1. **Preview**: Check your Google Sheets file structure
        2. **Process**: Run payroll slip generation
        3. **Monitor**: View processing statistics
        4. **Configure**: Adjust system settings
        """)
    
    # System status
    st.markdown("---")
    st.subheader("System Status")
    
    try:
        status = st.session_state.processor.get_overall_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Employees Processed", status.get('successfully_processed', 0))
        
        with col2:
            st.metric("Failed Processing", status.get('failed_processing', 0))
        
        with col3:
            st.metric("Total Sessions", status.get('total_sessions', 0))
        
        with col4:
            last_updated = status.get('last_updated', 'Never')
            if last_updated != 'Never':
                try:
                    dt = datetime.fromisoformat(last_updated)
                    last_updated = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            st.metric("Last Updated", last_updated)
        
    except Exception as e:
        st.error(f"Error getting system status: {e}")

def show_preview_page():
    """File preview page"""
    st.title("File Preview")
    st.markdown("Preview and validate your Google Sheets payroll data")
    
    # Input parameters
    col1, col2 = st.columns(2)
    
    with col1:
        google_file_id = st.text_input(
            "Google Sheets File ID",
            value=config.get_google_file_id(),
            help="ID of Google Sheets file with employee data"
        )
    
    with col2:
        sheet_name = st.text_input(
            "Sheet Name (optional)",
            value=config.get_default_sheet_name() or "",
            help="Leave empty for default sheet"
        )
    
    if st.button("Preview File", type="primary"):
        if not google_file_id:
            st.error("Please enter Google Sheets File ID")
            return
        
        with st.spinner("Downloading and analyzing file..."):
            try:
                preview_data = st.session_state.processor.preview_source_file(
                    google_file_id, sheet_name or None
                )
                
                if "error" in preview_data:
                    st.error(f"Error: {preview_data['error']}")
                    return
                
                # File information
                st.success(f"File loaded: {preview_data['original_name']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"File format: {preview_data['file_format']}")
                
                with col2:
                    if preview_data['sheets']:
                        st.info(f"Available sheets: {', '.join(preview_data['sheets'])}")
                
                # Validation results
                validation = preview_data['validation']
                if validation['valid']:
                    st.success(f"Validation passed: {validation['rows_with_id']} valid employee records found")
                else:
                    st.error(f"Validation failed: {validation['error']}")
                    if 'missing_required_columns' in validation:
                        st.error(f"Missing columns: {validation['missing_required_columns']}")
                    if 'found_columns' in validation:
                        st.info(f"Found columns: {validation['found_columns']}")
                    return
                
                # Preview data
                st.subheader("Data Preview")
                if preview_data['preview']:
                    df = pd.DataFrame(preview_data['preview'])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No preview data available")
                
                # Column information
                st.subheader("Column Information")
                st.write("Available columns:", preview_data['columns'])
                
            except Exception as e:
                st.error(f"Error previewing file: {e}")

def show_processing_page():
    """Payroll processing page"""
    st.title("Payroll Processing")
    st.markdown("Generate and upload payroll slips for all employees")
    
    # Input parameters
    col1, col2 = st.columns(2)
    
    with col1:
        google_file_id = st.text_input(
            "Google Sheets File ID",
            value=config.get_google_file_id(),
            help="ID of Google Sheets file with employee data"
        )
        
        google_folder_id = st.text_input(
            "Google Drive Folder ID (PDF)",
            value=config.get_google_folder_id(),
            help="ID of Google Drive folder for PDF uploads"
        )
        
        csv_folder_id = st.text_input(
            "Google Drive Folder ID (CSV)",
            value=config.get_csv_folder_id(),
            help="ID of Google Drive folder for CSV reports (optional)"
        )
    
    with col2:
        sheet_name = st.text_input(
            "Sheet Name (optional)",
            value=config.get_default_sheet_name() or "",
            help="Leave empty for default sheet"
        )
        
        force_recreate = st.checkbox(
            "Force Recreate",
            value=config.should_force_recreate(),
            help="Recreate payroll slips even if already processed"
        )
        
        generate_csv = st.checkbox(
            "Generate CSV Reports",
            value=config.should_generate_csv(),
            help="Generate CSV reports with PDF links and employee IDs"
        )
    
    # Processing controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Processing", type="primary"):
            if not google_file_id or not google_folder_id:
                st.error("Please enter both Google File ID and PDF Folder ID")
                return
            
            if generate_csv and not csv_folder_id:
                st.error("Please enter CSV Folder ID or disable CSV generation")
                return
            
            # Store processing parameters
            st.session_state.processing_params = {
                'google_file_id': google_file_id,
                'google_folder_id': google_folder_id,
                'csv_folder_id': csv_folder_id if generate_csv else None,
                'sheet_name': sheet_name or None,
                'force_recreate': force_recreate
            }
            st.session_state.start_processing = True
    
    with col2:
        if st.button("Stop Processing"):
            st.session_state.start_processing = False
            st.warning("Processing stopped by user")
    
    # Processing execution
    if st.session_state.get('start_processing', False):
        params = st.session_state.processing_params
        
        progress_container = st.container()
        
        with progress_container:
            st.info("Processing in progress...")
            
            try:
                with st.spinner("Processing payroll slips..."):
                    results = st.session_state.processor.process_payrolls_complete(
                        params['google_file_id'],
                        params['google_folder_id'],
                        params['sheet_name'],
                        params['force_recreate'],
                        params['csv_folder_id']
                    )
                
                # Processing completed
                st.session_state.start_processing = False
                
                # Display results
                st.success("Processing completed successfully!")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Employees", results['total_employees'])
                
                with col2:
                    st.metric("Successfully Processed", len(results['processed']))
                
                with col3:
                    st.metric("Skipped", len(results['skipped']))
                
                with col4:
                    st.metric("Failed", len(results['failed']))
                
                # Processing time
                if results['processing_time']:
                    st.info(f"Processing time: {results['processing_time']:.2f} seconds")
                
                # CSV reports info
                if results.get('csv_report_id'):
                    st.success(f"CSV reports generated and uploaded to Google Drive")
                elif results.get('csv_error'):
                    st.warning(f"CSV generation failed: {results['csv_error']}")
                
                # Detailed results
                if results['processed']:
                    st.subheader("Successfully Processed")
                    processed_df = pd.DataFrame(results['processed'])
                    st.dataframe(processed_df, use_container_width=True)
                
                if results['skipped']:
                    st.subheader("Skipped (Already Processed)")
                    skipped_df = pd.DataFrame(results['skipped'])
                    st.dataframe(skipped_df, use_container_width=True)
                
                if results['failed']:
                    st.subheader("Failed Processing")
                    failed_df = pd.DataFrame(results['failed'])
                    st.dataframe(failed_df, use_container_width=True)
                
            except Exception as e:
                st.session_state.start_processing = False
                st.error(f"Processing error: {e}")

def show_statistics_page():
    """Statistics and history page"""
    st.title("Processing Statistics")
    st.markdown("View processing history and system statistics")
    
    try:
        status = st.session_state.processor.get_overall_status()
        
        # Overall statistics
        st.subheader("Overall Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Employees Ever Processed", status.get('successfully_processed', 0))
            st.metric("Failed Processing Attempts", status.get('failed_processing', 0))
        
        with col2:
            st.metric("Total Processing Sessions", status.get('total_sessions', 0))
            success_rate = 0
            total = status.get('successfully_processed', 0) + status.get('failed_processing', 0)
            if total > 0:
                success_rate = (status.get('successfully_processed', 0) / total) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            last_updated = status.get('last_updated', 'Never')
            if last_updated != 'Never':
                try:
                    dt = datetime.fromisoformat(last_updated)
                    last_updated = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            st.metric("Last Updated", last_updated)
        
        # Recent sessions
        st.subheader("🕒 Recent Processing Sessions")
        
        recent_sessions = status.get('recent_sessions', [])
        if recent_sessions:
            sessions_data = []
            for session in recent_sessions:
                session_info = {
                    'Session ID': session.get('session_id', 'Unknown')[:8] + '...',
                    'Status': session.get('status', 'Unknown'),
                    'Source File': session.get('source_file_name', 'Unknown'),
                    'Total Employees': session.get('total_employees', 0),
                    'Processed': session.get('processed_count', 0),
                    'Failed': session.get('failed_count', 0),
                    'Started At': session.get('started_at', 'Unknown')
                }
                
                # Format datetime
                if session_info['Started At'] != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(session_info['Started At'])
                        session_info['Started At'] = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                sessions_data.append(session_info)
            
            sessions_df = pd.DataFrame(sessions_data)
            st.dataframe(sessions_df, use_container_width=True)
        else:
            st.info("No recent sessions found")
        
        # Status file information
        st.subheader("Status File Information")
        status_file = status.get('status_file', 'Unknown')
        st.info(f"Status file location: {status_file}")
        
        if os.path.exists(status_file):
            file_size = os.path.getsize(status_file)
            st.info(f"Status file size: {file_size} bytes")
        
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

def show_settings_page():
    """Settings and configuration page"""
    st.title("System Settings")
    st.markdown("Configure system parameters and manage data")
    
    # Configuration Management
    st.subheader("Configuration Management")
    
    # Create tabs for different configuration sections
    tab1, tab2, tab3 = st.tabs(["Google Drive Settings", "Processing Settings", "PDF Settings"])
    
    with tab1:
        st.markdown("**Google Drive Integration Settings**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            google_file_id = st.text_input(
                "Default Google Sheets File ID",
                value=config.get_google_file_id(),
                help="Default Google Sheets file ID with employee data"
            )
            
            google_folder_id = st.text_input(
                "Default Google Drive Folder ID (PDF)",
                value=config.get_google_folder_id(),
                help="Default Google Drive folder ID for PDF uploads"
            )
        
        with col2:
            csv_folder_id = st.text_input(
                "Default Google Drive Folder ID (CSV)",
                value=config.get_csv_folder_id(),
                help="Default Google Drive folder ID for CSV reports"
            )
            
            default_sheet_name = st.text_input(
                "Default Sheet Name",
                value=config.get_default_sheet_name() or "",
                help="Default sheet name for Excel files (leave empty for auto-detection)"
            )
        
        if st.button("Save Google Drive Settings", type="primary"):
            config.update({
                'google_file_id': google_file_id,
                'google_folder_id': google_folder_id,
                'csv_folder_id': csv_folder_id,
                'default_sheet_name': default_sheet_name if default_sheet_name else None
            })
            config.save_config()
            st.success("Google Drive settings saved successfully!")
    
    with tab2:
        st.markdown("**Processing Behavior Settings**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            force_recreate = st.checkbox(
                "Force Recreate by Default",
                value=config.should_force_recreate(),
                help="Always recreate payroll slips even if already processed"
            )
            
            generate_csv = st.checkbox(
                "Generate CSV Reports by Default",
                value=config.should_generate_csv(),
                help="Always generate CSV reports with PDF links"
            )
        
        with col2:
            cleanup_days = st.number_input(
                "Session Cleanup Days",
                min_value=1,
                max_value=365,
                value=config.get_cleanup_days(),
                help="Number of days to keep old processing sessions"
            )
        
        if st.button("Save Processing Settings", type="primary"):
            config.update({
                'processing_settings.force_recreate': force_recreate,
                'processing_settings.generate_csv': generate_csv,
                'processing_settings.cleanup_old_sessions_days': cleanup_days
            })
            config.save_config()
            st.success("Processing settings saved successfully!")
    
    with tab3:
        st.markdown("**PDF Generation Settings**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name",
                value=config.get_company_name(),
                help="Company name to display on payroll slips"
            )
            
            default_currency = st.selectbox(
                "Default Currency",
                options=["USD", "EUR", "RUB", "GBP"],
                index=["USD", "EUR", "RUB", "GBP"].index(config.get('pdf_settings.default_currency', 'USD')),
                help="Default currency for payroll calculations"
            )
        
        with col2:
            date_format = st.selectbox(
                "Date Format",
                options=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y"],
                index=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y"].index(config.get('pdf_settings.date_format', '%Y-%m-%d')),
                help="Date format for payroll slips"
            )
        
        if st.button("Save PDF Settings", type="primary"):
            config.update({
                'pdf_settings.company_name': company_name,
                'pdf_settings.default_currency': default_currency,
                'pdf_settings.date_format': date_format
            })
            config.save_config()
            st.success("PDF settings saved successfully!")
    
    # Configuration file management
    st.markdown("---")
    st.subheader("Configuration File Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Reset to Defaults"):
            config.reset_to_defaults()
            st.success("Configuration reset to defaults!")
            st.rerun()
    
    with col2:
        if st.button("Show Current Config"):
            st.json(config.get_all())
    
    with col3:
        st.info(f"Config file: config.json")
    
    # Data management
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clean Old Sessions"):
            try:
                st.session_state.processor.tracker.cleanup_old_sessions(30)
                st.success("Old sessions cleaned up")
            except Exception as e:
                st.error(f"Error cleaning sessions: {e}")
    
    with col2:
        employee_id = st.text_input("Employee ID to Reset")
        if st.button("Reset Employee Status"):
            if employee_id:
                try:
                    st.session_state.processor.reset_employee_status(employee_id)
                    st.success(f"Employee {employee_id} status reset")
                except Exception as e:
                    st.error(f"Error resetting employee: {e}")
            else:
                st.error("Please enter Employee ID")
    
    # System information
    st.subheader("System Information")
    
    system_info = {
        "Python Version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "Working Directory": os.getcwd(),
        "Status File": "processing_status.json",
        "Temporary Files": "Automatically cleaned up"
    }
    
    for key, value in system_info.items():
        st.info(f"**{key}**: {value}")

if __name__ == "__main__":
    main()
