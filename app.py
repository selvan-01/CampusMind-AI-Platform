from flask import Flask, render_template, request, redirect, session, url_for, send_file
import os
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.attendance_agent import low_attendance_agent
from scheduler.performance_agent import low_performance_agent
from scheduler.exam_reminder_agent import exam_reminder_agent

from config import MYSQL_CONFIG, UPLOAD_EXCEL_PATH, UPLOAD_DOC_PATH

from services.excel_service import (
    upload_students_excel,
    upload_attendance_excel,
    upload_marks_excel,
    upload_exam_excel
)

from services.pdf_service import extract_text_from_pdf
from services.result_pdf_service import generate_result_pdf
from services.insight_service import get_insights
from services.report_service import generate_insight_pdf

from ai.embeddings import create_embeddings
from ai.router import route_question
from services.email_service import send_email


# ================= APP INIT =================
app = Flask(__name__)
app.secret_key = "campusmind_secret_key"
app.permanent_session_lifetime = timedelta(days=7)


# ================= DATABASE =================
def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("""
            SELECT username, password, role, student_id
            FROM users
            WHERE username = %s
        """, (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["student_id"] = user["student_id"]

            if request.form.get("remember"):
                session.permanent = True

            if user["role"] == "admin":
                return redirect(url_for("admin"))
            elif user["role"] == "faculty":
                return redirect(url_for("faculty"))
            else:
                return redirect(url_for("student"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# ================= DASHBOARDS =================
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin.html", insights=get_insights())


'''@app.route("/faculty")
def faculty():
    if session.get("role") != "faculty":
        return redirect("/")
    return render_template("faculty.html")'''

@app.route("/faculty")
def faculty():
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Total Students
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()["total"]

    # 2️⃣ Average Attendance
    cursor.execute("""
        SELECT AVG(percentage) as avg_attendance
        FROM attendance
    """)
    avg_attendance = cursor.fetchone()["avg_attendance"] or 0

    # 3️⃣ Average Marks
    cursor.execute("""
        SELECT AVG(marks) as avg_marks
        FROM marks
    """)
    avg_marks = cursor.fetchone()["avg_marks"] or 0

    # 4️⃣ Students at Risk (marks < 40 OR attendance < 75)
    cursor.execute("""
    SELECT 
        s.name,
        m.subject,
        m.marks,
        a.percentage
        FROM students s
        LEFT JOIN marks m ON s.student_id = m.student_id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        WHERE m.marks < 40 OR a.percentage < 75
    """)

    risk_raw = cursor.fetchall()

    risk_students = []

    for r in risk_raw:
        reason = []

        if r["marks"] is not None and r["marks"] < 40:
            reason.append(f"Low Marks ({r['marks']}) in {r['subject']}")

        if r["percentage"] is not None and r["percentage"] < 75:
            reason.append(f"Low Attendance ({r['percentage']}%)")

        risk_students.append({
            "name": r["name"],
            "reason": " + ".join(reason)
        })


    # 5️⃣ Student List
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "faculty.html",
        total_students=total_students,
        avg_attendance=round(avg_attendance, 2),
        avg_marks=round(avg_marks, 2),
        risk_students=risk_students,
        students=students
    )
    

'''@app.route("/faculty")
def faculty():
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name, COUNT(a.id) as total_classes
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
    """)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("faculty_dashboard.html", data=data)'''

@app.route("/student")
def student():
    if session.get("role") != "student":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT semester, year, marks,
               CASE WHEN marks >= 40 THEN 'PASS' ELSE 'FAIL' END AS result
        FROM marks
        WHERE student_id = %s
        ORDER BY year DESC, semester DESC
        LIMIT 1
    """, (session["student_id"],))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("student.html", result=result)

'''@app.route("/admin/departments")
def admin_departments():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT department, COUNT(*) as total_students
        FROM students
        GROUP BY department
    """)
    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_departments.html",
        departments=departments
    )'''

@app.route("/admin/departments")
@app.route("/admin/department-dashboard")
def department_dashboard():

    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Total Students per Department
    cursor.execute("""
        SELECT department, COUNT(*) as total_students
        FROM students
        GROUP BY department
    """)
    student_count = cursor.fetchall()

    # 2️⃣ Average Marks per Department
    cursor.execute("""
        SELECT s.department, AVG(m.marks) as avg_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.department
    """)
    avg_marks = cursor.fetchall()

    # 3️⃣ Average Attendance per Department
    cursor.execute("""
        SELECT s.department, AVG(a.percentage) as avg_attendance
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.department
    """)
    avg_attendance = cursor.fetchall()

    # 4️⃣ Full Student List
    cursor.execute("""
        SELECT name, department, year
        FROM students
        ORDER BY department
    """)
    student_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "department_dashboard.html",
        student_count=student_count,
        avg_marks=avg_marks,
        avg_attendance=avg_attendance,
        student_list=student_list
    )


@app.route("/admin/attendance")
def admin_attendance():
    if session.get("role") != "admin":
        return redirect("/")

    dept = request.args.get("department")
    year = request.args.get("year")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if dept and year:
        cursor.execute("""
            SELECT s.name, a.subject, a.percentage
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            WHERE s.department=%s AND s.year=%s
        """, (dept, year))
        records = cursor.fetchall()
    else:
        records = []

    cursor.close()
    conn.close()

    return render_template(
        "admin_attendance.html",
        records=records
    )
'''@app.route("/admin/performance")
def admin_performance():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name, m.subject, m.marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
    """)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_performance.html",
        data=data
    )'''

@app.route("/admin/performance")
@app.route("/admin/performance-dashboard")
def performance_dashboard():

    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Full Marks Table
    cursor.execute("""
        SELECT s.name, s.department, s.year,
               m.subject, m.marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
    """)
    marks_data = cursor.fetchall()

    # 2️⃣ Subject-wise Average
    cursor.execute("""
        SELECT subject, AVG(marks) as avg_marks
        FROM marks
        GROUP BY subject
    """)
    subject_avg = cursor.fetchall()

    # 3️⃣ Department Average
    cursor.execute("""
        SELECT s.department, AVG(m.marks) as avg_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.department
    """)
    dept_avg = cursor.fetchall()

    # 4️⃣ Pass / Fail Count
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) as passed,
        SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) as failed
        FROM marks
    """)
    result_data = cursor.fetchone()

    # 5️⃣ Top 5 Toppers
    cursor.execute("""
        SELECT s.name, SUM(m.marks) as total_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        ORDER BY total_marks DESC
        LIMIT 5
    """)
    toppers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "performance_dashboard.html",
        marks_data=marks_data,
        subject_avg=subject_avg,
        dept_avg=dept_avg,
        result_data=result_data,
        toppers=toppers
    )

@app.route("/admin/faculty-dashboard")
def admin_faculty_dashboard():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get faculty list
    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()

    # Department count
    cursor.execute("""
        SELECT department, COUNT(*) as total
        FROM faculty
        GROUP BY department
    """)
    dept_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "faculty_dashboard.html",
        faculty=faculty_list,
        dept_data=dept_data
    )

@app.route("/admin/students")
def admin_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_students.html",
        students=students
    )
'''@app.route("/admin/attendance")
def attendance_dashboard():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.department, AVG(a.percentage) AS avg_attendance
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.department
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("attendance_dashboard.html", data=data)'''
@app.route("/admin/attendance-dashboard")
def attendance_dashboard():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Full Attendance Data
    cursor.execute("""
        SELECT s.name, s.department, s.year,
               a.subject, a.percentage
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
    """)
    attendance_data = cursor.fetchall()

    # 2️⃣ Department Average
    cursor.execute("""
        SELECT s.department, AVG(a.percentage) as avg_attendance
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.department
    """)
    dept_avg = cursor.fetchall()

    # 3️⃣ Low Attendance (<75%)
    cursor.execute("""
        SELECT s.name, s.department, a.percentage
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        WHERE a.percentage < 75
    """)
    low_attendance = cursor.fetchall()

    # 4️⃣ Overall Attendance
    cursor.execute("""
        SELECT AVG(percentage) as overall_avg
        FROM attendance
    """)
    overall = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "attendance_dashboard.html",
        attendance_data=attendance_data,
        dept_avg=dept_avg,
        low_attendance=low_attendance,
        overall=overall
    )

@app.route("/faculty/dashboard")
def faculty_dashboard():
    if session.get("role") != "faculty":
        return redirect("/")

    return render_template("faculty_dashboard.html")
@app.route("/admin/student/<int:student_id>")
def student_profile(student_id):
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    student = cursor.fetchone()

    cursor.execute("SELECT subject, percentage FROM attendance WHERE student_id=%s", (student_id,))
    attendance = cursor.fetchall()

    cursor.execute("SELECT subject, marks FROM marks WHERE student_id=%s", (student_id,))
    marks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "student_profile.html",
        student=student,
        attendance=attendance,
        marks=marks
    )
@app.route("/admin/student_dashboard")
def admin_student_dashboard():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ All Students
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    # 2️⃣ Department Count
    cursor.execute("""
        SELECT department, COUNT(*) as total
        FROM students
        GROUP BY department
    """)
    dept_data = cursor.fetchall()

    # 3️⃣ Pass / Fail Count
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) as passed,
        SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) as failed
        FROM marks
    """)
    result_data = cursor.fetchone()

    # 4️⃣ Year Distribution
    cursor.execute("""
        SELECT year, COUNT(*) as total
        FROM students
        GROUP BY year
    """)
    year_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "student_dashboard.html",
        students=students,
        dept_data=dept_data,
        result_data=result_data,
        year_data=year_data
    )
@app.route("/admin/users")
def admin_users():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, username, role, student_id FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_users.html", users=users)

@app.route("/admin/edit_user/<int:user_id>", methods=["GET","POST"])
def edit_user(user_id):
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]

        cursor.execute("""
            UPDATE users 
            SET username=%s, role=%s
            WHERE id=%s
        """, (username, role, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/admin/users")

    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("admin_edit_user.html", user=user)

@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin/users")

# ================= RESULT PDF =================
'''@app.route("/download_result")
def download_result():
    if session.get("role") != "student":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT s.student_id, s.name,
               m.semester, m.year, m.marks,
               CASE WHEN m.marks >= 40 THEN 'PASS' ELSE 'FAIL' END AS result
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        WHERE s.student_id = %s
        ORDER BY m.year DESC, m.semester DESC
        LIMIT 1
    """, (session["student_id"],))

    data = cursor.fetchone()
    cursor.close()
    conn.close()

    return send_file(generate_result_pdf(data, data), as_attachment=True)'''

# ================= DOWNLOAD INSIGHT REPORT =================
# ================= DOWNLOAD INSIGHT REPORT =================
@app.route("/download_insights")
def download_insights():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Total Students
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()["total"]

    # 2️⃣ Average Marks
    cursor.execute("SELECT AVG(marks) as avg_marks FROM marks")
    avg_marks = cursor.fetchone()["avg_marks"]

    # 3️⃣ Students at Risk
    cursor.execute("SELECT COUNT(*) as risk FROM marks WHERE marks < 40")
    risk_students = cursor.fetchone()["risk"]

    # 4️⃣ Pass / Fail
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) as passed,
        SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) as failed
        FROM marks
    """)
    result_data = cursor.fetchone()

    # 5️⃣ Department Breakdown
    cursor.execute("""
        SELECT department, COUNT(*) as total
        FROM students
        GROUP BY department
    """)
    dept_data = cursor.fetchall()

    # 6️⃣ Top 5 Toppers
    cursor.execute("""
        SELECT s.name, SUM(m.marks) as total_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        ORDER BY total_marks DESC
        LIMIT 5
    """)
    toppers = cursor.fetchall()

    cursor.close()
    conn.close()

    file_path = "insight_report.pdf"

    generate_insight_pdf(
        file_path,
        total_students,
        avg_marks,
        risk_students,
        result_data,
        dept_data,
        toppers
    )

    return send_file(file_path, as_attachment=True)


'''@app.route("/download_class_report")
def download_class_report():

    if session.get("role") not in ["admin", "faculty"]:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Total Students
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()["total"]

    # 2️⃣ Average Marks
    cursor.execute("SELECT AVG(marks) as avg_marks FROM marks")
    avg_marks = cursor.fetchone()["avg_marks"]

    # 3️⃣ Risk Students (marks < 40)
    cursor.execute("SELECT COUNT(*) as risk FROM marks WHERE marks < 40")
    risk_students = cursor.fetchone()["risk"]

    # 4️⃣ Pass / Fail
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) as passed,
        SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) as failed
        FROM marks
    """)
    result_data = cursor.fetchone()

    # 5️⃣ Department Breakdown
    cursor.execute("""
        SELECT department, COUNT(*) as total
        FROM students
        GROUP BY department
    """)
    dept_data = cursor.fetchall()

    # 6️⃣ Top 5 Toppers
    cursor.execute("""
        SELECT s.name, SUM(m.marks) as total_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        ORDER BY total_marks DESC
        LIMIT 5
    """)
    toppers = cursor.fetchall()

    cursor.close()
    conn.close()

    # File path
    file_path = "class_report.pdf"

    generate_insight_pdf(
        file_path,
        total_students,
        avg_marks,
        risk_students,
        result_data,
        dept_data,
        toppers
    )

    return send_file(file_path, as_attachment=True)'''

# ================= EXCEL UPLOADS =================
@app.route("/upload_students", methods=["POST"])
def upload_students():
    if session.get("role") != "faculty":
        return redirect("/")
    os.makedirs(UPLOAD_EXCEL_PATH, exist_ok=True)
    file = request.files["excel_file"]
    path = os.path.join(UPLOAD_EXCEL_PATH, file.filename)
    file.save(path)
    upload_students_excel(path)
    return "Students uploaded"


@app.route("/upload_attendance", methods=["POST"])
def upload_attendance():
    if session.get("role") != "faculty":
        return redirect("/")
    os.makedirs(UPLOAD_EXCEL_PATH, exist_ok=True)
    file = request.files["excel_file"]
    path = os.path.join(UPLOAD_EXCEL_PATH, file.filename)
    file.save(path)
    upload_attendance_excel(path)
    return "Attendance uploaded"


@app.route("/upload_marks", methods=["POST"])
def upload_marks():
    if session.get("role") != "faculty":
        return redirect("/")
    os.makedirs(UPLOAD_EXCEL_PATH, exist_ok=True)
    file = request.files["excel_file"]
    path = os.path.join(UPLOAD_EXCEL_PATH, file.filename)
    file.save(path)
    upload_marks_excel(path)
    return "Marks uploaded"


@app.route("/upload_exam", methods=["POST"])
def upload_exam():
    if session.get("role") != "faculty":
        return redirect("/")
    os.makedirs(UPLOAD_EXCEL_PATH, exist_ok=True)
    file = request.files["excel_file"]
    path = os.path.join(UPLOAD_EXCEL_PATH, file.filename)
    file.save(path)
    upload_exam_excel(path)
    return "Exam uploaded"


# ================= PDF + RAG =================
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if session.get("role") != "admin":
        return redirect("/")

    os.makedirs(UPLOAD_DOC_PATH, exist_ok=True)
    file = request.files["pdf_file"]
    path = os.path.join(UPLOAD_DOC_PATH, file.filename)
    file.save(path)

    text = extract_text_from_pdf(path)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    create_embeddings(chunks)

    return "PDF indexed"


# ================= CHATBOT =================
@app.route("/chat", methods=["POST"])
def chat():
    if not session.get("role"):
        return "Please login again."

    print("SESSION STUDENT_ID:", session.get("student_id"))

    question = request.form.get("question", "")
    return route_question(question, {
        "role": session["role"],
        "student_id": session["student_id"]
    })


# ================= ADMIN CREATE USER =================
@app.route("/admin/create_user", methods=["GET", "POST"])
def create_user():
    if session.get("role") != "admin":
        return redirect("/")

    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        student_id = request.form.get("student_id") or None

        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        cursor.execute("""
            INSERT INTO users (username, password, role, student_id)
            VALUES (%s, %s, %s, %s)
        """, (username, password, role, student_id))

        conn.commit()
        cursor.close()
        conn.close()

        return "✅ User created successfully"

    return render_template("admin_create_user.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route("/faculty/send-attendance-warning")
def send_attendance_warning():
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name, s.email, AVG(a.percentage) as avg_attendance
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
        HAVING avg_attendance < 65
    """)

    students = cursor.fetchall()
    cursor.close()
    conn.close()

    for student in students:
        body = f"""
        <h3>Attendance Warning</h3>
        <p>Dear {student['name']},</p>
        <p>Your attendance is below required level.</p>
        <p>Please improve immediately.</p>
        """

        send_email(student["email"], "Attendance Warning", body)

    return "Attendance Warning Emails Sent"


@app.route("/faculty/send-performance-warning")
def send_performance_warning():
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name, s.email, AVG(m.marks) as avg_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        HAVING avg_marks < 40
    """)

    students = cursor.fetchall()
    cursor.close()
    conn.close()

    for student in students:
        body = f"""
        <h3>Performance Warning</h3>
        <p>Dear {student['name']},</p>
        <p>Your academic performance is below passing criteria.</p>
        <p>Please contact your faculty advisor.</p>
        """

        send_email(student["email"], "Performance Warning", body)

    return "Performance Warning Emails Sent"

@app.route("/faculty/send-exam-reminder")
def send_exam_reminder():
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name, email FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    for student in students:
        body = f"""
        <h3>Exam Reminder</h3>
        <p>Dear {student['name']},</p>
        <p>Upcoming exams are scheduled soon.</p>
        <p>Please prepare well.</p>
        """

        send_email(student["email"], "Exam Reminder", body)

    return "Exam Reminder Sent"

'''@app.route("/faculty/download-class-report")
def download_class_report():
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT AVG(percentage) as avg_attendance FROM attendance")
    attendance = cursor.fetchone()["avg_attendance"]

    cursor.execute("SELECT AVG(marks) as avg_marks FROM marks")
    marks = cursor.fetchone()["avg_marks"]

    cursor.execute("""
        SELECT s.name, SUM(m.marks) as total_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        ORDER BY total_marks DESC
        LIMIT 5
    """)
    toppers = cursor.fetchall()

    cursor.close()
    conn.close()

    data = {
        "attendance": round(attendance or 0, 2),
        "marks": round(marks or 0, 2),
        "toppers": toppers
    }

    file_path = "class_report.pdf"
    generate_insight_pdf(data, file_path)

    return send_file(file_path, as_attachment=True)'''
@app.route("/download_class_report")
def download_class_report():

    if session.get("role") not in ["admin", "faculty"]:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Students
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()["total"]

    # Average Marks
    cursor.execute("SELECT AVG(marks) as avg_marks FROM marks")
    avg_marks = cursor.fetchone()["avg_marks"]

    # Risk Students
    cursor.execute("SELECT COUNT(*) as risk FROM marks WHERE marks < 40")
    risk_students = cursor.fetchone()["risk"]

    # Pass / Fail
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) as passed,
        SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) as failed
        FROM marks
    """)
    result_data = cursor.fetchone()

    # Department Breakdown
    cursor.execute("""
        SELECT department, COUNT(*) as total
        FROM students
        GROUP BY department
    """)
    dept_data = cursor.fetchall()

    # Top 5 Toppers
    cursor.execute("""
        SELECT s.name, SUM(m.marks) as total_marks
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        ORDER BY total_marks DESC
        LIMIT 5
    """)
    toppers = cursor.fetchall()

    cursor.close()
    conn.close()

    file_path = "class_report.pdf"

    generate_insight_pdf(
        file_path,
        total_students,
        avg_marks,
        risk_students,
        result_data,
        dept_data,
        toppers
    )

    return send_file(file_path, as_attachment=True)

# ================= SCHEDULER =================
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(low_attendance_agent, "interval", days=1)
scheduler.add_job(low_performance_agent, "interval", days=7)
scheduler.add_job(exam_reminder_agent, "interval", days=1)
scheduler.start()


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
