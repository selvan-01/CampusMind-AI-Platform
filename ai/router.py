import mysql.connector
from config import MYSQL_CONFIG
from ai.qa_bank import STUDENT_QA, FACULTY_QA, ADMIN_QA


def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


def route_question(question, user_context, intent=None):
    role = user_context.get("role")
    student_id = user_context.get("student_id")
    q = question.lower().strip()

    # ==================================================
    # 1️⃣ REAL-TIME STUDENT ATTENDANCE (SQL FIRST)
    # ==================================================
    if role == "student" and "attendance" in q:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT AVG(percentage) FROM attendance WHERE student_id = %s",
            (student_id,)
        )
        row = cur.fetchone()
        conn.close()

        if not row or row[0] is None:
            return "📊 Attendance data not available."

        return f"📊 Your attendance is {round(row[0], 2)}%"

    # ==================================================
    # 2️⃣ REAL-TIME STUDENT MARKS
    # ==================================================
    if role == "student" and ("mark" in q or "result" in q):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT marks FROM marks WHERE student_id = %s ORDER BY year DESC LIMIT 1",
            (student_id,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return "📝 Marks not published yet."

        status = "PASS ✅" if row[0] >= 40 else "FAIL ❌"
        return f"📝 Your marks: {row[0]} ({status})"

    # ==================================================
    # 3️⃣ ADMIN REAL-TIME DATA
    # ==================================================
    if role == "admin" and "total student" in q:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        total = cur.fetchone()[0]
        conn.close()

        return f"👨‍💼 Total students: {total}"

    # ==================================================
    # 4️⃣ STATIC QA (ONLY IF NOT REAL-TIME)
    # ==================================================
    if role == "student":
        for key, answer in STUDENT_QA.items():
            if key in q:
                return answer

    if role == "faculty":
        for key, answer in FACULTY_QA.items():
            if key in q:
                return answer

    if role == "admin":
        for key, answer in ADMIN_QA.items():
            if key in q:
                return answer

    return "❓ Please ask about attendance, marks, or academic information."
