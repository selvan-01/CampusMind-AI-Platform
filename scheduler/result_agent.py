import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from config import MYSQL_CONFIG
from services.email_service import send_email


def result_agent():
    print("\n📢 Result Agent Started")

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT 
            s.name,
            s.email,
            m.student_id,
            m.marks,
            m.semester,
            m.year
        FROM marks m
        JOIN students s ON s.student_id = m.student_id
        WHERE m.result_published = FALSE
    """)

    rows = cursor.fetchall()

    if not rows:
        print("ℹ️ No new results to publish.")
        cursor.close()
        conn.close()
        return

    for r in rows:
        status = "PASS" if r["marks"] >= 40 else "FAIL"

        print(
            f"📄 Result processed → {r['email']} | "
            f"Marks: {r['marks']} | Status: {status}"
        )

        try:
            send_email(
                r["email"],
                "📢 Semester Examination Result",
                f"""
Dear {r['name']},

Your semester examination result has been published.

Semester : {r['semester']}
Year     : {r['year']}
Marks    : {r['marks']}
Status   : {status}

Regards,
CampusMind Examination Cell
"""
            )
        except Exception as e:
            print(f"⚠️ Email failed for {r['email']} | Reason: {e}")

        cursor.execute(
            "UPDATE marks SET result_published = TRUE WHERE student_id = %s",
            (r["student_id"],)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Result Agent Completed\n")


if __name__ == "__main__":
    result_agent()
