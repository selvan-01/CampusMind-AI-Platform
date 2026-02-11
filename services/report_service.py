from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import matplotlib.pyplot as plt
import os


def generate_insight_pdf(path, total_students, avg_marks, risk_students,
                         result_data, dept_data, toppers):

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # =========================
    # CUSTOM STYLES
    # =========================
    title_style = styles["Title"]
    heading_style = ParagraphStyle(
        name="HeadingCustom",
        parent=styles["Heading2"],
        textColor=colors.darkblue
    )

    # =========================
    # TITLE
    # =========================
    elements.append(
        Paragraph("<b>CampusMind Academic Insight Report</b>", title_style)
    )
    elements.append(Spacer(1, 25))

    # =========================
    # SUMMARY SECTION
    # =========================
    elements.append(Paragraph("Academic Summary", heading_style))
    elements.append(Spacer(1, 10))

    passed = result_data['passed'] or 0
    failed = result_data['failed'] or 0

    summary_data = [
        ["Metric", "Value"],
        ["Total Students", total_students],
        ["Average Marks", round(avg_marks or 0, 2)],
        ["Students at Risk", risk_students],
        ["Passed", passed],
        ["Failed", failed]
    ]

    summary_table = Table(summary_data, colWidths=[250, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 25))

    # =========================
    # DEPARTMENT BREAKDOWN
    # =========================
    elements.append(Paragraph("Department Breakdown", heading_style))
    elements.append(Spacer(1, 10))

    dept_table_data = [["Department", "Total Students"]]
    for d in dept_data:
        dept_table_data.append([d['department'], d['total']])

    dept_table = Table(dept_table_data, colWidths=[250, 150])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(dept_table)
    elements.append(Spacer(1, 25))

    # =========================
    # TOP 5 TOPPERS
    # =========================
    elements.append(Paragraph("Top 5 Toppers", heading_style))
    elements.append(Spacer(1, 10))

    topper_data = [["Name", "Total Marks"]]
    for t in toppers:
        topper_data.append([t['name'], t['total_marks']])

    topper_table = Table(topper_data, colWidths=[250, 150])
    topper_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(topper_table)
    elements.append(Spacer(1, 25))

    # =========================
    # PASS / FAIL PIE CHART
    # =========================
    plt.figure(figsize=(4, 4))
    plt.pie(
        [passed, failed],
        labels=["Passed", "Failed"],
        autopct='%1.1f%%',
        colors=["#2ecc71", "#e74c3c"]
    )
    plt.title("Pass / Fail Distribution")

    chart_path = "pass_fail_chart.png"
    plt.savefig(chart_path)
    plt.close()

    elements.append(Paragraph("Performance Chart", heading_style))
    elements.append(Spacer(1, 10))
    elements.append(Image(chart_path, width=4 * inch, height=4 * inch))
    elements.append(Spacer(1, 20))

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)

    # Cleanup image file
    if os.path.exists(chart_path):
        os.remove(chart_path)

    return path
