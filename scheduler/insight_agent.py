import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from config import MYSQL_CONFIG


def insight_agent():
    print("\n🧠 Insight Agent Started\n")

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True, buffered=True)

    # 1️⃣ Average attendance by department
    cursor.execute("""
        SELECT s.department, AVG(a.percentage) AS avg_attendance
        FROM attendance a
        JOIN students s ON s.student_id = a.student_id
        GROUP BY s.department
    """)
    attendance_insight = cursor.fetchall()

    # 2️⃣ Students at academic risk
    cursor.execute("""
        SELECT COUNT(*) AS risk_count
        FROM marks
        WHERE marks < 40
    """)
    risk_students = cursor.fetchone()

    # 3️⃣ Overall performance average
    cursor.execute("""
        SELECT AVG(marks) AS avg_marks
        FROM marks
    """)
    avg_marks = cursor.fetchone()

    # 4️⃣ Total students
    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM students
    """)
    total_students = cursor.fetchone()

    cursor.close()
    conn.close()

    # 📊 PRINT INSIGHTS
    print("📊 COLLEGE INSIGHTS REPORT\n")

    print(f"👥 Total Students           : {total_students['total_students']}")
    print(f"📈 Overall Avg Marks        : {round(avg_marks['avg_marks'], 2)}")
    print(f"⚠️ Students at Risk (<40)  : {risk_students['risk_count']}\n")

    print("🏫 Department-wise Attendance:")
    for d in attendance_insight:
        print(f"   - {d['department']} : {round(d['avg_attendance'], 2)}%")

    print("\n✅ Insight Agent Completed\n")


if __name__ == "__main__":
    insight_agent()
