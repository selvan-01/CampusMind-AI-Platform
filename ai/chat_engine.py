from config import MYSQL_CONFIG
import mysql.connector


def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


def handle_admin_faculty(question):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    question = question.lower()

    # Who failed?
    if "failed" in question:
        cursor.execute("""
            SELECT s.name, m.subject, m.marks
            FROM students s
            JOIN marks m ON s.student_id = m.student_id
            WHERE m.marks < 40
        """)
        data = cursor.fetchall()
        conn.close()

        if not data:
            return "No failed students."

        return "<br>".join(
            [f"{d['name']} failed {d['subject']} ({d['marks']})" for d in data]
        )

    # Attendance of department
    if "attendance" in question:
        cursor.execute("""
            SELECT s.department, AVG(a.percentage) as avg_att
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.department
        """)
        data = cursor.fetchall()
        conn.close()

        return "<br>".join(
            [f"{d['department']} average attendance: {round(d['avg_att'],2)}%"
             for d in data]
        )

    conn.close()
    return "I couldn't understand the question."


def handle_student(question, student_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    question = question.lower()

    if "marks" in question:
        cursor.execute("""
            SELECT subject, marks
            FROM marks
            WHERE student_id=%s
        """, (student_id,))
        data = cursor.fetchall()
        conn.close()

        return "<br>".join(
            [f"{d['subject']}: {d['marks']}" for d in data]
        )

    if "attendance" in question:
        cursor.execute("""
            SELECT subject, percentage
            FROM attendance
            WHERE student_id=%s
        """, (student_id,))
        data = cursor.fetchall()
        conn.close()

        return "<br>".join(
            [f"{d['subject']}: {d['percentage']}%" for d in data]
        )

    conn.close()
    return "You can only access your own academic data."
