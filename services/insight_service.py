import mysql.connector
from config import MYSQL_CONFIG


def get_insights():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Total students
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]

    # Average marks
    cursor.execute("SELECT AVG(marks) AS avg_marks FROM marks")
    avg_marks = cursor.fetchone()["avg_marks"]

    # Students at risk
    cursor.execute("SELECT COUNT(*) AS risk FROM marks WHERE marks < 40")
    risk_students = cursor.fetchone()["risk"]

    # Department-wise attendance
    cursor.execute("""
        SELECT s.department, AVG(a.percentage) AS avg_attendance
        FROM attendance a
        JOIN students s ON s.student_id = a.student_id
        GROUP BY s.department
    """)
    dept_attendance = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_students": total_students,
        "avg_marks": round(avg_marks, 2) if avg_marks else 0,
        "risk_students": risk_students,
        "dept_attendance": dept_attendance
    }
def get_insight_text():
    insights = get_insights()

    text = f"""
College Insights Summary:

Total Students: {insights['total_students']}
Average Marks: {insights['avg_marks']}
Students at Risk: {insights['risk_students']}

Department-wise Attendance:
"""

    for d in insights["dept_attendance"]:
        text += f"- {d['department']}: {round(d['avg_attendance'], 2)}%\n"

    return text
