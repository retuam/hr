# 💰 Automated Payroll Processing System

A comprehensive system for automated payroll slip generation from Google Sheets data with PDF creation and Google Drive integration.

## 🎯 Features

- **📥 Google Drive Integration**: Download payroll data directly from Google Sheets
- **📄 Professional PDF Generation**: Create detailed payroll slips with calculations
- **☁️ Automated Upload**: Upload generated PDFs to organized Google Drive folders
- **📊 Progress Tracking**: Monitor processing status and avoid duplicates
- **🌐 Web Interface**: User-friendly Streamlit web application
- **🔄 Smart Processing**: Skip already processed employees or force recreation
- **📈 Statistics Dashboard**: View processing history and system metrics

## 🏗️ System Architecture

### Core Components

1. **Google Drive Downloader** (`english_google_drive_downloader.py`)
   - Downloads Google Sheets as Excel files
   - Handles authentication and file conversion

2. **Local File Handler** (`english_local_file_handler.py`)
   - Processes Excel/CSV files locally
   - Validates data structure and extracts employee information

3. **PDF Generator** (`english_pdf_generator.py`)
   - Creates professional payroll slips
   - Includes calculation methodology and signatures

4. **Google Drive Handler** (`english_google_drive_handler.py`)
   - Uploads PDFs to Google Drive
   - Creates date-based folder organization

5. **Processing Tracker** (`english_processing_tracker.py`)
   - Maintains JSON log of processed employees
   - Tracks sessions and prevents duplicates

6. **Final Processor** (`final_english_processor.py`)
   - Orchestrates the complete workflow
   - Handles error management and reporting

7. **Streamlit Interface** (`final_english_streamlit_app.py`)
   - Web-based user interface
   - Authentication, preview, processing, and statistics

## 📋 Data Structure

The system expects Google Sheets with the following columns:

### Required Columns
- `id` - Employee ID (unique identifier)
- `name` - Employee full name
- `base` - Base salary amount

### Optional Columns
- `location` - Employee location
- `% from base` - Percentage from base salary
- `payment` - Payment amount
- `base periods` - Number of base periods
- `bonus usd` - Bonus amount in USD
- `sla` - SLA performance percentage
- `sla bonus` - SLA bonus amount
- `total usd` - Total amount in USD
- `rate` - Exchange rate
- `total rub` - Total amount in RUB
- `total rub rounded` - Rounded total in RUB

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account
- Google Drive API enabled
- Google Sheets API enabled

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hrproject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google API credentials**
   - Create a service account in Google Cloud Console
   - Download the JSON credentials file
   - Enable Google Drive API and Google Sheets API

4. **Set up environment variables**
   Create a `.env` file with:
   ```env
   GOOGLE_CREDENTIALS_FILE=path/to/your/credentials.json
   GOOGLE_FILE_ID=your_google_sheets_file_id
   GOOGLE_FOLDER=your_google_drive_folder_id
   ```

## 🖥️ Usage

### Web Interface (Recommended)

1. **Start the Streamlit application**
   ```bash
   streamlit run final_english_streamlit_app.py
   ```

2. **Access the web interface**
   - Open your browser to `http://localhost:8501`
   - Login with credentials: `admin` / `admin`

3. **Use the interface**
   - **Home**: System overview and status
   - **File Preview**: Validate your Google Sheets data
   - **Process Payrolls**: Run the complete processing cycle
   - **Statistics**: View processing history and metrics
   - **Settings**: Configure system parameters

### Command Line Usage

```python
from final_english_processor import FinalEnglishPayrollProcessor

# Initialize processor
processor = FinalEnglishPayrollProcessor()

# Preview file
preview = processor.preview_source_file('your_google_file_id')

# Process payrolls
results = processor.process_payrolls_complete(
    google_file_id='your_google_file_id',
    google_folder_id='your_google_folder_id',
    force_recreate=False
)
```

## 📁 File Structure

```
hrproject/
├── final_english_processor.py          # Main processing orchestrator
├── final_english_streamlit_app.py      # Web interface
├── english_google_drive_downloader.py  # Google Drive file downloader
├── english_local_file_handler.py       # Local file processing
├── english_pdf_generator.py            # PDF generation
├── english_google_drive_handler.py     # Google Drive upload handler
├── english_processing_tracker.py       # Processing status tracker
├── requirements.txt                     # Python dependencies
├── .env                                # Environment variables
├── processing_status.json              # Processing status log (auto-created)
└── README_ENGLISH.md                   # This documentation
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CREDENTIALS_FILE` | Path to Google service account JSON | `./credentials.json` |
| `GOOGLE_FILE_ID` | Default Google Sheets file ID | `1abc...xyz` |
| `GOOGLE_FOLDER` | Default Google Drive folder ID | `1def...uvw` |

### Processing Options

- **Force Recreate**: Regenerate PDFs even if already processed
- **Sheet Name**: Specify Excel sheet name (optional)
- **Custom Folders**: Use different Google Drive folders per session

## 📊 Processing Flow

1. **Download**: Fetch Google Sheets file from Google Drive
2. **Validate**: Check file structure and required columns
3. **Extract**: Parse employee data from the file
4. **Generate**: Create PDF payroll slips for each employee
5. **Upload**: Save PDFs to Google Drive with date-based organization
6. **Track**: Log processing status to prevent duplicates

## 🛡️ Security

- **Authentication**: Simple admin/admin authentication for web interface
- **Credentials**: Google API credentials stored in separate JSON file
- **Environment**: Sensitive data in environment variables
- **Temporary Files**: Automatic cleanup of temporary files

## 📈 Monitoring

### Processing Status
- JSON-based tracking of all processed employees
- Session management with unique IDs
- Error logging and retry capabilities

### Statistics Dashboard
- Success/failure rates
- Processing time metrics
- Recent session history
- Employee processing status

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Google API credentials file path
   - Check API permissions and enabled services

2. **File Access Errors**
   - Ensure service account has access to Google Sheets file
   - Verify Google Drive folder permissions

3. **Data Validation Errors**
   - Check required columns are present
   - Verify employee ID format and uniqueness

4. **PDF Generation Errors**
   - Check file system permissions
   - Verify ReportLab installation

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the system logs

## 🔄 Version History

- **v1.0.0**: Initial release with basic functionality
- **v1.1.0**: Added web interface and statistics
- **v1.2.0**: Enhanced error handling and logging
- **v2.0.0**: Complete English translation and improved architecture

---

**Note**: This system is designed for internal payroll processing. Ensure compliance with local data protection and payroll regulations.
