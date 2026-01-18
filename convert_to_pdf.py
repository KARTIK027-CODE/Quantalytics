#!/usr/bin/env python3
"""
Convert Markdown presentation guide to PDF
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import re

def parse_markdown_to_pdf(md_file, pdf_file):
    """Convert markdown to PDF with formatting"""
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leftIndent=20,
        fontName='Helvetica'
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        textColor=colors.HexColor('#c7254e'),
        backColor=colors.HexColor('#f9f2f4'),
        fontName='Courier'
    )
    
    # Story (content container)
    story = []
    
    # Split content into lines
    lines = content.split('\n')
    
    # Process lines
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Title (first H1)
        if line.startswith('# ') and i < 5:
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 0.3*inch))
            i += 1
            continue
        
        # H2 headers
        if line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, h1_style))
            i += 1
            continue
        
        # H3 headers
        if line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, h2_style))
            i += 1
            continue
        
        # H4 headers
        if line.startswith('#### '):
            text = line[5:].strip()
            story.append(Paragraph(text, h3_style))
            i += 1
            continue
        
        # Horizontal rules
        if line.startswith('---'):
            story.append(Spacer(1, 0.2*inch))
            i += 1
            continue
        
        # Tables
        if line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            
            # Parse table
            if len(table_lines) > 2:  # Header + separator + data
                rows = []
                for tline in table_lines:
                    if '---' not in tline:  # Skip separator
                        cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                        rows.append(cells)
                
                if rows:
                    # Create table
                    t = Table(rows)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 0.2*inch))
            continue
        
        # Bullet points
        if line.startswith('- ') or line.startswith('* ') or line.startswith('✓ '):
            text = line[2:].strip()
            # Handle bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Handle italic
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            # Handle code
            text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
            story.append(Paragraph('• ' + text, bullet_style))
            i += 1
            continue
        
        # Numbered lists
        if re.match(r'^\d+\.', line):
            text = re.sub(r'^\d+\.\s*', '', line)
            # Handle bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Handle italic
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            # Handle code
            text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
            story.append(Paragraph(line, bullet_style))
            i += 1
            continue
        
        # Regular paragraphs
        text = line
        # Handle bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Handle italic
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Handle code
        text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
        
        story.append(Paragraph(text, body_style))
        i += 1
    
    # Build PDF
    doc.build(story)
    print(f"✓ PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    md_file = "Presentation_Speaking_Guide.md"
    pdf_file = "Team_NeoQuant_Presentation_Guide.pdf"
    
    try:
        parse_markdown_to_pdf(md_file, pdf_file)
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying to install reportlab...")
        import subprocess
        subprocess.run(["pip3", "install", "reportlab"], check=True)
        print("Retrying PDF generation...")
        parse_markdown_to_pdf(md_file, pdf_file)
