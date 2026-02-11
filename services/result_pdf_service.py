from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def generate_result_pdf(student, result):
    filename = f"result_{student['student_id']}.pdf"
    path = os.path.join("static", "results", filename)

    os.makedirs("static/results", exist_ok=True)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "MOTHER TERESA COLLEGE OF ENGINEERING AND TECHNOLOGY")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Name       : {student['name']}")
    c.drawString(50, height - 130, f"Semester   : {result['semester']}")
    c.drawString(50, height - 160, f"Year       : {result['year']}")
    c.drawString(50, height - 190, f"Marks      : {result['marks']}")
    c.drawString(50, height - 220, f"Result     : {result['result']}")

    c.drawString(50, height - 280, "Authorized by CampusMind AI Examination Cell")

    c.save()
    return path
