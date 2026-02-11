import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from config import MYSQL_CONFIG
from services.email_service import send_email


def low_performance_agent():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Find students with low marks and not yet notified
    cursor.execute("""
        SELECT s.email, s.name, m.marks, m.student_id
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        WHERE m.marks < 40 AND m.performance_mail_sent = FALSE
    """)

    students = cursor.fetchall()

    for s in students:
        send_email(
            s["email"],
            "Academic Performance Alert",
            f"""
Dear {s['name']},

Your recent exam performance is below the expected level.

Marks Scored: {s['marks']}

Please consult your faculty and focus on improvement.
CampusMind AI is here to support your learning journey.

Regards,
CampusMind Academic System
"""
        )

        # Mark email as sent
        cursor.execute(
            "UPDATE marks SET performance_mail_sent = TRUE WHERE student_id = %s",
            (s["student_id"],)
        )

    conn.commit()
    cursor.close()
    conn.close()


# Manual test
if __name__ == "__main__":
    low_performance_agent()
