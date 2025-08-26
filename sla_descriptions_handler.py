"""
SLA Descriptions Handler
Загружает описания методологии расчетов из Google Sheets по SLA ID
"""

import pandas as pd
from typing import Dict, Optional
from google_drive_downloader import GoogleDriveDownloader
from config_manager import config


class SLADescriptionsHandler:
    def __init__(self):
        """Initialize SLA descriptions handler"""
        self.descriptions_cache = {}
        self.downloader = GoogleDriveDownloader()
        
    def get_description_by_sla_id(self, sla_id: int) -> str:
        """
        Get methodology description by SLA ID
        
        Args:
            sla_id: SLA ID number
            
        Returns:
            Methodology text or default text if not found
        """
        try:
            # Load descriptions if not cached
            if not self.descriptions_cache:
                self._load_descriptions()
            
            # Get description by SLA ID
            description = self.descriptions_cache.get(sla_id)
            if description:
                print(f"📋 Найдено описание для SLA ID {sla_id}")
                return description
            else:
                print(f"⚠️ Описание для SLA ID {sla_id} не найдено, используем по умолчанию")
                return self._get_default_description()
                
        except Exception as e:
            print(f"❌ Ошибка получения описания для SLA ID {sla_id}: {e}")
            return self._get_default_description()
    
    def _load_descriptions(self):
        """Load SLA descriptions from Google Sheets"""
        try:
            print("📥 Загружаем SLA descriptions из Google Sheets...")
            
            # Get SLA descriptions file ID from config
            sla_file_id = config.get_sla_descriptions_file_id()
            if not sla_file_id:
                print("⚠️ SLA descriptions file ID не настроен в конфиге")
                return
            
            # Download file
            temp_file_path, original_name = self.downloader.download_to_temp_file(sla_file_id)
            print(f"📁 Загружен файл: {original_name}")
            
            # Read Excel file
            df = pd.read_excel(temp_file_path)
            print(f"📊 Загружено {len(df)} строк из SLA descriptions")
            
            # Parse data: expect columns "SLA ID" and "TEXT"
            for index, row in df.iterrows():
                sla_id = row.get('SLA ID')
                text = row.get('TEXT', '')
                
                if pd.notna(sla_id) and text:
                    try:
                        sla_id_int = int(sla_id)
                        self.descriptions_cache[sla_id_int] = str(text).strip()
                        print(f"✅ Загружено описание для SLA ID {sla_id_int}")
                    except (ValueError, TypeError):
                        print(f"⚠️ Некорректный SLA ID: {sla_id}")
            
            print(f"📋 Всего загружено описаний: {len(self.descriptions_cache)}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки SLA descriptions: {e}")
    
    def _get_default_description(self) -> str:
        """Get default methodology description"""
        return """
        <b>Base Salary Calculation:</b><br/>
        The base salary is calculated according to the employee's contract and position level.
        
        <br/><br/><b>Bonus Calculation:</b><br/>
        • Performance bonuses are calculated based on individual and team performance metrics<br/>
        • SLA bonuses are awarded for meeting or exceeding service level agreements<br/>
        • Additional bonuses may be awarded for exceptional performance or special projects
        
        <br/><br/><b>SLA Criteria:</b><br/>
        • SLA ≥ 95%: Full SLA bonus<br/>
        • SLA 90-94%: 75% of SLA bonus<br/>
        • SLA 85-89%: 50% of SLA bonus<br/>
        • SLA < 85%: No SLA bonus
        
        <br/><br/><b>Currency Conversion:</b><br/>
        All calculations are performed in USD and converted to RUB using the current exchange rate.
        The final amount is rounded to the nearest whole ruble.
        
        <br/><br/><b>Deductions:</b><br/>
        This payroll slip shows gross amounts before any tax deductions or other withholdings.
        Net amounts will be calculated separately according to applicable tax regulations.
        """
    
    def reload_descriptions(self):
        """Force reload descriptions from Google Sheets"""
        self.descriptions_cache.clear()
        self._load_descriptions()
