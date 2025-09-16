# # employee/utils/pdf_generator.py

# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from io import BytesIO
# from django.utils import timezone

# def generate_employee_details_pdf(employee):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
#     styles = getSampleStyleSheet()
#     styleN = styles['Normal']
#     styleH = styles['Heading1']
#     styleH2 = styles['Heading2']

#     # Custom style for smaller heading
#     small_heading = ParagraphStyle(
#         'SmallHeading',
#         parent=styles['Heading2'],
#         fontSize=10,
#         spaceAfter=6
#     )

#     story = []

#     # Title
#     story.append(Paragraph(f"Employee Details: {employee.full_name}", styleH))
#     story.append(Spacer(1, 12))

#     # Basic Info Table
#     data = [
#         ["Field", "Value"],
#         ["Employee ID", employee.employee_id],
#         ["Full Name", employee.full_name],
#         ["Email", employee.email or "N/A"],
#         ["Gender", employee.get_gender_display() or "N/A"],
#         ["Date of Birth", employee.date_of_birth.strftime('%Y-%m-%d') if employee.date_of_birth else "N/A"],
#         ["Blood Group", employee.blood_group or "N/A"],
#         ["Joining Date", employee.joining_date.strftime('%Y-%m-%d')],
#         ["Permanent Date", employee.permanent_date.strftime('%Y-%m-%d') if employee.permanent_date else "N/A"],
#         ["Designation", str(employee.designation) if employee.designation else "N/A"],
#         ["Phone", employee.phone or "N/A"],
#         ["Address", employee.address or "N/A"],
#         ["Present Address", employee.present_address or "N/A"],
#         ["National ID", employee.national_id_no or "N/A"],
#         ["TIN Number", employee.tax_info or "N/A"],
#         ["Is TPM", "Yes" if employee.is_tpm else "No"],
#         ["Tax Eligible", "Yes" if employee.tax_eligible else "No"],
#         ["Manager", "Yes" if employee.manager else "No"],
#         ["Lead", "Yes" if employee.lead else "No"],
#         ["SQA", "Yes" if employee.sqa else "No"],
#         ["Active", "Yes" if employee.active else "No"],
#         ["Operation", "Yes" if employee.operation else "No"],
#         ["Lunch Allowance", "Yes" if employee.lunch_allowance else "No"],
#         ["Project Eligibility", "Yes" if employee.project_eligibility else "No"],
#         ["Leave in Cash Eligibility", "Yes" if employee.leave_in_cash_eligibility else "No"],
#         ["PF Eligibility", "Yes" if employee.pf_eligibility else "No"],
#         ["Festival Bonus Eligibility", "Yes" if employee.festival_bonus_eligibility else "No"],
#         ["Device Allowance", "Yes" if employee.device_allowance else "No"],
#         ["Entry Pass ID", employee.entry_pass_id or "N/A"],
#         ["Monthly Expected Hours", f"{employee.monthly_expected_hours}" if employee.monthly_expected_hours else "N/A"],
#     ]

#     table = Table(data, colWidths=[2*inch, 4*inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0,0), (1,0), colors.grey),
#         ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
#         ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#         ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0,0), (-1,-1), 8),
#         ('BOTTOMPADDING', (0,0), (-1,0), 12),
#         ('BACKGROUND', (0,1), (-1,-1), colors.beige),
#         ('GRID', (0,0), (-1,-1), 1, colors.black),
#     ]))
#     story.append(table)
#     story.append(Spacer(1, 12))

#     # Salary History
#     salary_histories = employee.salaryhistory_set.all().order_by('-active_from')
#     if salary_histories:
#         story.append(Paragraph("Salary History", small_heading))
#         salary_data = [["Payable Salary", "Effective From", "Note"]]
#         for sh in salary_histories:
#             salary_data.append([
#                 str(sh.payable_salary),
#                 sh.active_from.strftime('%Y-%m-%d') if sh.active_from else "N/A",
#                 sh.note or "N/A"
#             ])
#         salary_table = Table(salary_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
#         salary_table.setStyle(TableStyle([
#             ('BACKGROUND', (0,0), (-1,0), colors.grey),
#             ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
#             ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#             ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0,0), (-1,-1), 8),
#             ('BOTTOMPADDING', (0,0), (-1,0), 12),
#             ('BACKGROUND', (0,1), (-1,-1), colors.beige),
#             ('GRID', (0,0), (-1,-1), 1, colors.black),
#         ]))
#         story.append(salary_table)
#         story.append(Spacer(1, 12))

#     # Skills
#     top_skills = employee.top_skills
#     if top_skills:
#         story.append(Paragraph("Top Skills", small_heading))
#         skill_data = [["Skill", "Percentage"]]
#         for skill in top_skills:
#             skill_data.append([skill.skill.title if skill.skill else "N/A", f"{skill.percentage}%"])
#         skill_table = Table(skill_data, colWidths=[3*inch, 3*inch])
#         skill_table.setStyle(TableStyle([
#             ('BACKGROUND', (0,0), (-1,0), colors.grey),
#             ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
#             ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#             ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0,0), (-1,-1), 8),
#             ('BOTTOMPADDING', (0,0), (-1,0), 12),
#             ('BACKGROUND', (0,1), (-1,-1), colors.beige),
#             ('GRID', (0,0), (-1,-1), 1, colors.black),
#         ]))
#         story.append(skill_table)
#         story.append(Spacer(1, 12))

#     # Bank Accounts
#     bank_accounts = employee.bankaccount_set.all()
#     if bank_accounts:
#         story.append(Paragraph("Bank Accounts", small_heading))
#         bank_data = [["Bank Name", "Account Number", "Branch", "Default"]]
#         for ba in bank_accounts:
#             bank_data.append([
#                 ba.bank.name if ba.bank else "N/A",
#                 ba.account_number or "N/A",
#                 ba.branch or "N/A",
#                 "Yes" if ba.default else "No"
#             ])
#         bank_table = Table(bank_data, colWidths=[2*inch, 2*inch, 1.5*inch, 0.5*inch])
#         bank_table.setStyle(TableStyle([
#             ('BACKGROUND', (0,0), (-1,0), colors.grey),
#             ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
#             ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#             ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0,0), (-1,-1), 8),
#             ('BOTTOMPADDING', (0,0), (-1,0), 12),
#             ('BACKGROUND', (0,1), (-1,-1), colors.beige),
#             ('GRID', (0,0), (-1,-1), 1, colors.black),
#         ]))
#         story.append(bank_table)
#         story.append(Spacer(1, 12))

#     # Attachments
#     attachments = employee.attachment_set.all()
#     if attachments:
#         story.append(Paragraph("Attachments", small_heading))
#         for att in attachments:
#             story.append(Paragraph(f"📄 {att.file_name.name}: {att.file.url if att.file else 'No file'}", styleN))
#         story.append(Spacer(1, 12))

#     # Generated at
#     story.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Italic']))

#     doc.build(story)
#     buffer.seek(0)
#     return buffer




# employee/utils/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from django.utils import timezone
import os

def generate_employee_details_pdf(employee):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )
    styles = getSampleStyleSheet()

    # === CUSTOM STYLES ===
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=14,
        textColor=colors.HexColor("#2C3E50"),
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#7F8C8D"),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        # textColor=colors.white,
        # backColor=colors.HexColor("#3498DB"),
        spaceBefore=15,
        spaceAfter=10,
        alignment=TA_LEFT
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        fontName='Helvetica-Bold'
    )

    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#333333"),
        spaceAfter=6
    )

    small_text = ParagraphStyle(
        'Small',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
        spaceBefore=20
    )

    story = []

    # === HEADER ===
    # Optional: Add Company Logo (uncomment and adjust path if you have one)
    # logo_path = os.path.join(settings.STATIC_ROOT, "images", "company_logo.png")
    # if os.path.exists(logo_path):
    #     logo = Image(logo_path, width=1.5*inch, height=0.75*inch)
    #     logo.hAlign = 'CENTER'
    #     story.append(logo)
    #     story.append(Spacer(1, 10))

    story.append(Paragraph("Employee Information Dossier", title_style))
    story.append(Paragraph("Official Record — For Internal Use Only", subtitle_style))

    # === PERSONAL INFORMATION ===
    story.append(Paragraph("Personal Information", section_header))

    personal_data = [
        ("Full Name", employee.full_name),
        ("Employee ID", employee.employee_id),
        ("Gender", employee.get_gender_display() or "—"),
        ("Date of Birth", employee.date_of_birth.strftime('%d %B %Y') if employee.date_of_birth else "—"),
        ("Blood Group", employee.blood_group or "—"),
        ("National ID", employee.national_id_no or "—"),
        ("TIN Number", employee.tax_info or "—"),
        ("Joining Date", employee.joining_date.strftime('%d %B %Y')),
        ("Permanent Date", employee.permanent_date.strftime('%d %B %Y') if employee.permanent_date else "Not Permanent"),
    ]

    for label, value in personal_data:
        story.append(Paragraph(f"<b>{label}:</b> {value}", value_style))

    story.append(Spacer(1, 10))

    # === CONTACT INFORMATION ===
    story.append(Paragraph("Contact & Address", section_header))

    contact_data = [
        ("Email", employee.email or "—"),
        ("Phone", employee.phone or "—"),
        ("Permanent Address", employee.address or "—"),
        ("Present Address", employee.present_address or "—"),
    ]

    for label, value in contact_data:
        story.append(Paragraph(f"<b>{label}:</b> {value}", value_style))

    story.append(Spacer(1, 10))

    # === PROFESSIONAL INFORMATION ===
    story.append(Paragraph("Professional Details", section_header))

    prof_data = [
        ("Designation", str(employee.designation) if employee.designation else "—"),
        ("Department", str(employee.designation.department) if employee.designation and hasattr(employee.designation, 'department') else "—"),
        ("Reporting To", "Manager" if employee.manager else "Lead" if employee.lead else "—"),
        ("Is TPM", "Yes" if employee.is_tpm else "No"),
        ("Project Eligible", "Yes" if employee.project_eligibility else "No"),
        ("Leave in Cash Eligible", "Yes" if employee.leave_in_cash_eligibility else "No"),
        ("Tax Eligible", "Yes" if employee.tax_eligible else "No"),
        ("PF Eligible", "Yes" if employee.pf_eligibility else "No"),
        ("Festival Bonus Eligible", "Yes" if employee.festival_bonus_eligibility else "No"),
        ("Lunch Allowance", "Yes" if employee.lunch_allowance else "No"),
        ("Device Allowance", "Yes" if employee.device_allowance else "No"),
        ("Status", "Active" if employee.active else "Inactive"),
        ("Entry Pass ID", employee.entry_pass_id or "—"),
        ("Expected Monthly Hours", f"{employee.monthly_expected_hours} hrs" if employee.monthly_expected_hours else "—"),
    ]

    for label, value in prof_data:
        story.append(Paragraph(f"<b>{label}:</b> {value}", value_style))

    story.append(Spacer(1, 10))

    # === SALARY HISTORY ===
    # === SALARY HISTORY ===
    salary_histories = employee.salaryhistory_set.all().order_by('-active_from')
    if salary_histories:
        story.append(Paragraph("Salary History", section_header))

        # Only use fields that exist in YOUR SalaryHistory model
        salary_table_data = [["Effective From", "Payable Salary", "Note"]]
        for sh in salary_histories:
            salary_table_data.append([
                sh.active_from.strftime('%d %b %Y') if sh.active_from else "—",
                f"{sh.payable_salary:,.0f}" if sh.payable_salary else "—",  # ✅ Only use payable_salary
                sh.note or "—"
            ])

        salary_table = Table(salary_table_data, colWidths=[1.5*inch, 2*inch, 3*inch])  # Adjusted widths
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#441ADB")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8F9FA")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(salary_table)
        story.append(Spacer(1, 10))


    # === BANK ACCOUNTS ===
    bank_accounts = employee.bankaccount_set.all()
    if bank_accounts:
        story.append(Paragraph("Bank Accounts", section_header))

        bank_table_data = [["Bank", "Account Number", "Default"]]
        for ba in bank_accounts:
            bank_name = ba.bank.name if ba.bank else "—"
            bank_table_data.append([
                bank_name,
                ba.account_number or "—",
                "✓" if ba.default else "—"
            ])

        bank_table = Table(bank_table_data, colWidths=[2*inch, 2*inch, 1.5*inch, 0.5*inch])
        bank_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#441ADB")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8F9FA")),
        ]))
        story.append(bank_table)
        story.append(Spacer(1, 10))

        # === SOCIAL MEDIA PROFILES ===
    employee_socials = employee.employeesocial_set.all()
    if employee_socials:
        story.append(Paragraph("Social Media & Profiles", section_header))

        social_table_data = [["Platform", "Profile URL"]]
        for es in employee_socials:
            # Get platform name: from SocialMedia if linked, else from title field
            platform = "—"
            if es.social_name and es.social_name.title:
                platform = es.social_name.title
            elif es.title:
                platform = es.title

            # Make URL clickable in PDF (if viewer supports it)
            url = es.url or "—"
            display_url = url if len(url) < 50 else url[:47] + "..."
            social_table_data.append([
                platform,
                f"{display_url}" if url != "—" else "—"
            ])

        social_table = Table(social_table_data, colWidths=[1.5*inch, 4.5*inch])
        social_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#441ADB")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8F9FA")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TEXTCOLOR', (1,1), (-1,-1), colors.blue),  # Links in blue
        ]))
        story.append(social_table)
        story.append(Spacer(1, 10))

    # === ATTACHMENTS ===
    attachments = employee.attachment_set.all()
    if attachments:
        story.append(Paragraph("📎 Attachments", section_header))
        for att in attachments:
            file_name = att.file_name.name if att.file_name else "Unnamed Document"
            file_url = att.file.url if att.file else "#"
            story.append(Paragraph(f"📄 <a href='{file_url}' color='blue'>{file_name}</a>", value_style))
        story.append(Spacer(1, 10))

    # === FOOTER ===
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated on {timezone.now().strftime('%d %B %Y at %H:%M')} by HR System", small_text))
    story.append(Paragraph("© 2025 Mediusware LTD. Confidential and Proprietary.", small_text))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer