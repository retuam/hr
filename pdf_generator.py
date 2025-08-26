"""
Module for generating PDF payroll slips
Creates detailed payroll documents with calculations and methodology
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any

class PayrollPDFGenerator:
    def __init__(self):
        """Initialize PDF generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        print("📄 PDF generator initialized")
    
    def _setup_custom_styles(self):
        """Setup custom styles for PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        # Small text style
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            textColor=colors.grey
        )
    
    def generate_payroll_pdf(self, employee: Dict[str, Any], output_path: str):
        """
        Generate payroll PDF for employee matching the required layout
        
        Args:
            employee: Employee data dictionary
            output_path: Path to save PDF
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            # Build content
            story = []
            
            # Header with gray background
            story.extend(self._create_header_section(employee))
            story.append(Spacer(1, 30))
            
            # Employee info section
            story.extend(self._create_employee_section(employee))
            story.append(Spacer(1, 30))
            
            # Bonus calculation section
            story.extend(self._create_bonus_section(employee))
            story.append(Spacer(1, 30))
            
            # Base calculation section
            story.extend(self._create_base_section(employee))
            story.append(Spacer(1, 30))
            
            # SLA descriptions section
            story.extend(self._create_sla_section())
            
            # Build PDF
            doc.build(story)
            print(f"✅ PDF generated: {output_path}")
            
        except Exception as e:
            raise Exception(f"Error generating PDF: {e}")
    
    def _create_header_section(self, employee: Dict[str, Any]) -> list:
        """Create header section with gray background"""
        content = []
        
        # Gray header with "Bonuses list"
        header_table = Table([["Bonuses list"]], colWidths=[7*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        content.append(header_table)
        return content
    
    def _create_employee_section(self, employee: Dict[str, Any]) -> list:
        """Create employee information section"""
        content = []
        
        # Employee info table
        # Get calculation period from employee data or use current quarter
        from datetime import datetime
        current_date = datetime.now()
        quarter = f"Q{((current_date.month - 1) // 3) + 1}, {current_date.year}"
        calculation_period = employee.get('calculation_period', quarter)
        
        employee_data = [
            ["EMPLOYEE NAME", "CALCULATION PERIOD"],
            [str(employee.get('name', 'N/A')), calculation_period]
        ]
        
        employee_table = Table(employee_data, colWidths=[3*inch, 3*inch])
        employee_table.setStyle(TableStyle([
            # Header row
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data row
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('TOPPADDING', (0, 1), (-1, 1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
            
            # Lines
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        content.append(employee_table)
        return content
    
    def _create_bonus_section(self, employee: Dict[str, Any]) -> list:
        """Create bonus calculation section"""
        content = []
        
        # Section title
        title = Paragraph("<b>Bonus calculation</b>", 
                         ParagraphStyle('BonusTitle', fontSize=16, alignment=TA_CENTER, spaceAfter=20))
        content.append(title)
        
        # Bonus table headers
        bonus_headers = [
            "Type of bonus",
            "% of SLA achievement*", 
            "Bonus, $",
            "Bonus fin, $",
            "Bonus in local currency",
            "Calculation period"
        ]
        
        # Bonus data - get real values from employee data
        sla_percent = employee.get('sla', 0) * 100  # Convert to percentage
        bonus_usd = employee.get('bonus_usd', 0)  # This should be 52 from "Bonus USD" column
        bonus_usd_fin = employee.get('bonus_usd_fin', 0)  # This should be 41 from "Bonus USD fin" column
        bonus_local = employee.get('total_rub', 0)  # This should be 3,766 from "Bonus loc cur" column
        
        print(f"🔍 PDF ГЕНЕРАТОР - ОТЛАДКА ДАННЫХ:")
        print(f"   sla_percent: {sla_percent}")
        print(f"   bonus_usd: {bonus_usd} (тип: {type(bonus_usd)})")
        print(f"   bonus_usd_fin: {bonus_usd_fin} (тип: {type(bonus_usd_fin)})")
        print(f"   bonus_local: {bonus_local} (тип: {type(bonus_local)})")
        print(f"   Все данные employee: {employee}")
        
        print(f"   ✅ ФИНАЛЬНЫЕ ЗНАЧЕНИЯ ДЛЯ PDF:")
        print(f"      bonus_usd: {bonus_usd}")
        print(f"      bonus_usd_fin: {bonus_usd_fin}")
        
        # Проверяем что именно попадает в PDF таблицу
        print(f"   📋 ЧТО ПОПАДАЕТ В PDF ТАБЛИЦУ:")
        print(f"      Bonus USD, $: ${bonus_usd:.0f}")
        print(f"      Bonus USD fin, $: ${bonus_usd_fin:.0f}")
        
        bonus_data = [
            bonus_headers,
            [
                "Bonus from SLA",
                f"{sla_percent:.0f}%",
                f"${bonus_usd:.0f}",
                f"${bonus_usd_fin:.0f}",
                f"₽{bonus_local:,.0f}",
                "Quarter"
            ]
        ]
        
        bonus_table = Table(bonus_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.8*inch, 1.3*inch])
        bonus_table.setStyle(TableStyle([
            # Header row - gray text, smaller font
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),
            
            # Data row - normal text
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            
            # NO BORDERS! Only thin separator line under header
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.lightgrey),
            
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        content.append(bonus_table)
        return content
    
    def _create_base_section(self, employee: Dict[str, Any]) -> list:
        """Create base calculation section"""
        content = []
        
        # Section title
        title = Paragraph("<b>Base for calculation</b>", 
                         ParagraphStyle('BaseTitle', fontSize=16, alignment=TA_CENTER, spaceAfter=20))
        content.append(title)
        
        # Base calculation data - use real values
        base_amount = employee.get('base', 0)
        percent_from_base = employee.get('percent_from_base', 0)
        
        # Get company name from employee data
        company_name = employee.get('company', employee.get('location', 'Company'))
        
        base_data = [
            ["BASE", company_name],
            ["% from the base", f"{percent_from_base*100:.3f}%"],
            ["Base in $", f"{base_amount:,.0f}"]
        ]
        
        base_table = Table(base_data, colWidths=[2*inch, 3*inch])
        base_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            
            # NO BORDERS! Only thin horizontal lines between rows
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.lightgrey),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.lightgrey),
            
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        content.append(base_table)
        return content
    
    def _create_sla_section(self) -> list:
        """Create SLA descriptions section"""
        content = []
        
        # Section title
        title = Paragraph("<b>SLA Descriptions</b>", 
                         ParagraphStyle('SLATitle', fontSize=16, alignment=TA_CENTER, spaceAfter=20))
        content.append(title)
        
        # Real SLA methodology - single text block, small gray font
        sla_text = """SLA Calculation Methodology:

Key Performance Indicators:
• Analytics Standards: All sites with GA and YM must comply with standards
• Sprint Task Completion: Percentage of tasks moved from 'In Progress' to 'Done'
• Dashboard Functionality: Working dashboard in each launched business unit

Color Coding System:
• Green: All standards met, 100% completion, fully functional dashboards
• Yellow: Minor issues resolved within 2 weeks, 90-99% completion
• Red: Data loss/restrictions, <90% completion, missing dashboards >1 week

Variable Pay Access Rules:
• 100% - All Green indicators
• 75% - 2 Green, 1 Yellow
• 50% - 2 Yellow, 1 Green
• 0% - More than 1 Red indicator"""
        
        # Create single table cell with all text
        sla_table = Table([[sla_text]], colWidths=[6*inch])
        sla_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),  # Smaller font
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),  # Gray color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            # NO BORDERS! Only thin outer border like in example
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        content.append(sla_table)
        return content
    
    def _create_payroll_calculations_section(self, employee: Dict[str, Any]) -> list:
        """Create payroll calculations section"""
        content = []
        
        content.append(Paragraph("PAYROLL CALCULATIONS", self.header_style))
        
        # Calculations table
        calc_data = [
            ["Description", "Amount (USD)", "Amount (RUB)"],
            ["Base Salary", f"${employee.get('base', 0):.2f}", ""],
            ["Bonus USD", f"${employee.get('bonus_usd', 0):.2f}", ""],
            ["Bonus USD fin", f"${employee.get('bonus_usd_fin', 0):.2f}", ""],
            ["SLA Bonus", f"${employee.get('sla_bonus', 0):.2f}", ""],
            ["", "", ""],
            ["Total USD", f"${employee.get('total_usd', 0):.2f}", ""],
            ["Exchange Rate", f"{employee.get('rate', 0):.2f}", ""],
            ["Bonus loc cur", "", f"₽{employee.get('total_rub', 0):.2f}"],
            ["Total RUB (Rounded)", "", f"₽{employee.get('total_rub_rounded', 0):.0f}"]
        ]
        
        calc_table = Table(calc_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        calc_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Total rows highlighting
            ('BACKGROUND', (0, 5), (-1, 5), colors.lightyellow),
            ('BACKGROUND', (0, 7), (-1, 8), colors.lightgreen),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTNAME', (0, 7), (-1, 8), 'Helvetica-Bold'),
        ]))
        
        content.append(calc_table)
        
        # Additional info
        content.append(Spacer(1, 10))
        content.append(Paragraph(
            f"<b>SLA Performance:</b> {employee.get('sla', 0):.1f}%",
            self.normal_style
        ))
        content.append(Paragraph(
            f"<b>Base Periods:</b> {employee.get('base_periods', 0):.1f}",
            self.normal_style
        ))
        content.append(Paragraph(
            f"<b>Percent from Base:</b> {employee.get('percent_from_base', 0)*100:.3f}%",
            self.normal_style
        ))
        
        return content
    
    def _create_methodology_section(self) -> list:
        """Create calculation methodology section"""
        content = []
        
        content.append(Paragraph("CALCULATION METHODOLOGY", self.header_style))
        
        methodology_text = """
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
        
        content.append(Paragraph(methodology_text, self.normal_style))
        return content
    
    def _create_signature_section(self) -> list:
        """Create signature section"""
        content = []
        
        content.append(Spacer(1, 30))
        
        # Signature table
        signature_data = [
            ["Prepared by:", "_" * 30, "Date:", datetime.now().strftime("%d.%m.%Y")],
            ["", "", "", ""],
            ["Approved by:", "_" * 30, "Date:", "_" * 15],
            ["", "", "", ""],
            ["Employee signature:", "_" * 30, "Date:", "_" * 15]
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 2*inch, 0.8*inch, 1.2*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        content.append(signature_table)
        
        # Footer
        content.append(Spacer(1, 20))
        content.append(Paragraph(
            f"Generated on {datetime.now().strftime('%d.%m.%Y at %H:%M')}",
            self.small_style
        ))
        content.append(Paragraph(
            "This document is automatically generated and contains confidential information.",
            self.small_style
        ))
        
        return content

if __name__ == "__main__":
    # Testing
    generator = PayrollPDFGenerator()
    
    # Test employee data - remove hardcoded values
    test_employee = {
        'id': '001',
        'name': 'Test Employee',
        'location': 'Test Location',
        'base': 0.0,
        'bonus_usd': 0.0,
        'sla': 0.0,
        'sla_bonus': 0.0,
        'total_usd': 0.0,
        'rate': 0.0,
        'total_rub': 0.0,
        'total_rub_rounded': 0.0,
        'base_periods': 0.0,
        'percent_from_base': 0.0
    }
    
    # Generate test PDF
    output_file = "test_payroll_slip.pdf"
    
    try:
        generator.generate_payroll_pdf(test_employee, output_file)
        print(f"✅ Test PDF generated: {output_file}")
    except Exception as e:
        print(f"❌ Error generating test PDF: {e}")
