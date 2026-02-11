import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from datetime import date
from config import MYSQL_CONFIG
from services.email_service import send_email


def exam_reminder_agent():
    print("\n🚀 Exam Reminder Agent Started")
    today = date.today()

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True, buffered=True)

    # 🔥 One exam → many students (department + year based)
    cursor.execute("""
        SELECT 
            e.id,
            e.subject,
            e.exam_date,
            e.department,
            e.year,
            s.email,
            s.name
        FROM exam_schedule e
        JOIN students s
          ON s.department = e.department
         AND s.year = e.year
        WHERE e.reminder_sent = FALSE
    """)

    rows = cursor.fetchall()

    if not rows:
        print("ℹ️ No pending exam reminders found.")
        cursor.close()
        conn.close()
        return

    processed_exam_ids = set()
    triggered_count = 0

    for row in rows:
        days_left = (row["exam_date"] - today).days

        if days_left in [7, 1]:
            print(
                f"🔔 Reminder triggered → {row['email']} | "
                f"{row['department']} Year {row['year']} | {row['subject']}"
            )

            try:
                send_email(
                    row["email"],
                    "📅 Exam Reminder",
                    f"""
Dear {row['name']},

This is a reminder for your upcoming examination.

Subject      : {row['subject']}
Department   : {row['department']}
Year         : {row['year']}
Exam Date    : {row['exam_date']}
Days Left    : {days_left}

Please prepare well.

Regards,
CampusMind Examination Cell
"""
                )
            except Exception as e:
                print(f"⚠️ Email failed for {row['email']} | Reason: {e}")

            processed_exam_ids.add(row["id"])
            triggered_count += 1

    # 🔒 Mark reminder sent (once per exam)
    for exam_id in processed_exam_ids:
        cursor.execute(
            "UPDATE exam_schedule SET reminder_sent = TRUE WHERE id = %s",
            (exam_id,)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Exam Reminder Agent Completed")
    print(f"📊 Total students processed: {triggered_count}\n")


# Manual test
if __name__ == "__main__":
    exam_reminder_agent()
