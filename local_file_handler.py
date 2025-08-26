"""
Module for processing local Excel/CSV files
Reads employee data from various file formats
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional

class LocalFileHandler:
    def __init__(self):
        """Initialize local file handler"""
        self.required_columns = ['id', 'name', 'base']
        print("📁 Local file handler initialized")
    
    def detect_file_format(self, file_path: str) -> str:
        """
        Detect file format by extension
        
        Args:
            file_path: Path to file
            
        Returns:
            File format: 'excel', 'csv', 'tsv', 'unknown'
        """
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension in ['.xlsx', '.xls']:
            return 'excel'
        elif extension == '.csv':
            return 'csv'
        elif extension in ['.tsv', '.txt']:
            return 'tsv'
        else:
            return 'unknown'
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Get sheet names for Excel files
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List of sheet names
        """
        try:
            if self.detect_file_format(file_path) == 'excel':
                excel_file = pd.ExcelFile(file_path)
                return excel_file.sheet_names
            else:
                return []
        except Exception as e:
            print(f"⚠️ Error getting sheet names: {e}")
            return []
    
    def read_file(self, file_path: str, sheet_name: str = None) -> pd.DataFrame:
        """
        Read file into DataFrame
        
        Args:
            file_path: Path to file
            sheet_name: Sheet name (for Excel files)
            
        Returns:
            DataFrame with file data
        """
        file_format = self.detect_file_format(file_path)
        
        try:
            if file_format == 'excel':
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file_path)
            elif file_format == 'csv':
                df = pd.read_csv(file_path)
            elif file_format == 'tsv':
                df = pd.read_csv(file_path, sep='\t')
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
            
            # Clean column names
            df.columns = df.columns.str.strip().str.lower()
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def validate_file_structure(self, file_path: str, sheet_name: str = None) -> Dict[str, Any]:
        """
        Validate file structure and required columns
        
        Args:
            file_path: Path to file
            sheet_name: Sheet name (for Excel files)
            
        Returns:
            Validation results
        """
        try:
            df = self.read_file(file_path, sheet_name)
            
            # Check if file is empty
            if df.empty:
                return {
                    'valid': False,
                    'error': 'File is empty',
                    'total_rows': 0,
                    'rows_with_id': 0
                }
            
            # Check required columns
            missing_columns = []
            for col in self.required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return {
                    'valid': False,
                    'error': f'Missing required columns: {missing_columns}',
                    'missing_required_columns': missing_columns,
                    'found_columns': list(df.columns),
                    'total_rows': len(df),
                    'rows_with_id': 0
                }
            
            # Count rows with ID
            rows_with_id = len(df[df['id'].notna() & (df['id'] != '')])
            
            if rows_with_id == 0:
                return {
                    'valid': False,
                    'error': 'No rows with valid ID found',
                    'total_rows': len(df),
                    'rows_with_id': 0
                }
            
            return {
                'valid': True,
                'total_rows': len(df),
                'rows_with_id': rows_with_id,
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records')
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'total_rows': 0,
                'rows_with_id': 0
            }
    
    def preview_file(self, file_path: str, sheet_name: str = None, rows: int = 5) -> pd.DataFrame:
        """
        Preview first few rows of file
        
        Args:
            file_path: Path to file
            sheet_name: Sheet name (for Excel files)
            rows: Number of rows to preview
            
        Returns:
            DataFrame with preview data
        """
        try:
            df = self.read_file(file_path, sheet_name)
            return df.head(rows)
        except Exception as e:
            print(f"❌ Error previewing file: {e}")
            return pd.DataFrame()
    
    def get_employee_data(self, file_path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        Extract employee data from file
        
        Args:
            file_path: Path to file
            sheet_name: Sheet name (for Excel files)
            
        Returns:
            List of employee dictionaries
        """
        try:
            df = self.read_file(file_path, sheet_name)
            
            print(f"📊 ДАННЫЕ ИЗ GOOGLE SHEETS:")
            print(f"   📁 Файл: {file_path}")
            print(f"   📋 Лист: {sheet_name or 'по умолчанию'}")
            print(f"   📏 Всего строк: {len(df)}")
            print(f"   📊 Колонки: {list(df.columns)}")
            
            # Show first few rows
            print(f"\n🔍 ПЕРВЫЕ 3 СТРОКИ:")
            for i, (idx, row) in enumerate(df.head(3).iterrows()):
                print(f"   Строка {i+1}:")
                for col in df.columns:
                    print(f"      {col}: {row[col]}")
                print()
            
            # Filter rows with valid ID
            df_filtered = df[df['id'].notna() & (df['id'] != '')].copy()
            print(f"📋 После фильтрации по ID: {len(df_filtered)} строк")
            
            employees = []
            
            for row_num, (_, row) in enumerate(df_filtered.iterrows(), 1):
                print(f"\n👤 ОБРАБОТКА СОТРУДНИКА #{row_num}:")
                print(f"   📝 Исходные данные строки:")
                for col in df.columns:
                    print(f"      {col}: '{row[col]}' (тип: {type(row[col])})")
                employee = {
                    'id': str(row['id']).strip(),
                    'name': str(row.get('name', '')).strip(),
                    'base': self._safe_float(row.get('base jan-mar', 0)),  # Base Jan-Mar: 152,555
                    'location': str(row.get('location', '')).strip(),
                    'percent_from_base': self._safe_float(row.get('% from the base', 0)),  # % from the base: 0.034%
                    'payment': self._safe_float(row.get('payment', 0)),  # Payment: 4
                    'base_periods': self._safe_float(row.get('base periods', 0)),
                    'bonus_usd': self._safe_float(row.get('bonus usd fin', 0)),  # Bonus USD fin: 41
                    'sla': self._safe_float(row.get('sla', 0)),  # SLA: 80.00%
                    'sla_bonus': self._safe_float(row.get('sla bonus', 0)),
                    'total_usd': self._safe_float(row.get('total usd', 0)),
                    'rate': self._safe_float(row.get('rate', 90.8)),
                    'total_rub': self._safe_float(row.get('bonus loc cur', 0)),  # Bonus loc cur: 3,766
                    'total_rub_rounded': self._safe_float(row.get('bonus loc cur', 0))  # Убираем округление
                }
                
                print(f"   ✅ Обработанные данные сотрудника:")
                for key, value in employee.items():
                    print(f"      {key}: {value}")
                
                # Calculate missing fields if needed (БЕЗ ОКРУГЛЕНИЙ!)
                if not employee['total_usd'] and employee['base'] and employee['bonus_usd']:
                    employee['total_usd'] = employee['base'] + employee['bonus_usd']
                    print(f"   🧮 Рассчитал total_usd: {employee['total_usd']}")
                
                # Если total_rub уже есть из bonus loc cur, используем его как есть
                if not employee['total_rub'] and employee['total_usd'] and employee['rate']:
                    employee['total_rub'] = employee['total_usd'] * employee['rate']
                    print(f"   🧮 Рассчитал total_rub: {employee['total_rub']}")
                
                # total_rub_rounded теперь равен total_rub БЕЗ округления
                if employee['total_rub']:
                    employee['total_rub_rounded'] = employee['total_rub']
                    print(f"   ✅ total_rub_rounded = total_rub (без округления): {employee['total_rub_rounded']}")
                
                print(f"   ✅ ФИНАЛЬНЫЕ ДАННЫЕ ДЛЯ PDF:")
                for key, value in employee.items():
                    print(f"      {key}: {value}")
                
                employees.append(employee)
            
            print(f"👥 Extracted {len(employees)} employees from file")
            return employees
            
        except Exception as e:
            raise Exception(f"Error extracting employee data: {e}")
    
    def _safe_float(self, value) -> float:
        """
        Safely convert value to float
        
        Args:
            value: Value to convert
            
        Returns:
            Float value or 0.0
        """
        try:
            if pd.isna(value) or value == '':
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0

if __name__ == "__main__":
    # Testing
    handler = LocalFileHandler()
    
    # Test with sample file
    test_file = "sample_payroll.xlsx"
    
    if os.path.exists(test_file):
        print(f"🧪 Testing with file: {test_file}")
        
        # Validation
        validation = handler.validate_file_structure(test_file)
        print(f"📋 Validation: {validation}")
        
        if validation['valid']:
            # Preview
            preview = handler.preview_file(test_file)
            print(f"👀 Preview:\n{preview}")
            
            # Get employee data
            employees = handler.get_employee_data(test_file)
            print(f"👥 Found {len(employees)} employees")
            
            if employees:
                print(f"🔍 First employee: {employees[0]}")
        else:
            print("❌ File validation failed")
    else:
        print(f"❌ Test file not found: {test_file}")
