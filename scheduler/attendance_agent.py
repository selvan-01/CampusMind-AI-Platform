
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from config import MYSQL_CONFIG
from services.email_service import send_email


def low_attendance_agent():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT s.email, a.percentage
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        WHERE a.percentage < 75
    """)

    students = cursor.fetchall()
    cursor.close()
    conn.close()

    for s in students:
        send_email(
            s["email"],
            "Low Attendance Alert",
            f"Your attendance is {s['percentage']}%. Please improve."
        )

#if __name__ == "__main__":
    #low_attendance_agent()
