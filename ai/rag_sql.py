import mysql.connector
import ollama
from config import MYSQL_CONFIG


def ask_sql(question, user_context):
    q = question.lower()
    role = user_context.get("role")
    student_id = user_context.get("student_id")

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True, buffered=True)

        # =========================
        # 🔐 STUDENT SAFETY CHECK
        # =========================
        if role == "student" and not student_id:
            return "❌ Student identity not linked."

        # =========================
        # 1️⃣ ATTENDANCE
        # =========================
        if "attendance" in q:

            # 🎓 STUDENT → own attendance
            if role == "student":
                cursor.execute("""
                    SELECT month, year, percentage
                    FROM attendance
                    WHERE student_id = %s
                    ORDER BY year DESC, month DESC
                    LIMIT 3
                """, (student_id,))

                rows = cursor.fetchall()
                if not rows:
                    return "Attendance data not available."

                return "\n".join(
                    [f"{r['month']} {r['year']} → {r['percentage']}%"
                     for r in rows]
                )

            # 👨‍🏫 FACULTY / 👑 ADMIN → low attendance list
            else:
                cursor.execute("""
                    SELECT s.name, a.percentage
                    FROM attendance a
                    JOIN students s ON a.student_id = s.student_id
                    ORDER BY a.percentage ASC
                    LIMIT 5
                """)

                rows = cursor.fetchall()
                if not rows:
                    return "Attendance data not available."

                return "📉 Low Attendance Students:\n" + "\n".join(
                    [f"{r['name']} → {r['percentage']}%"
                     for r in rows]
                )

        # =========================
        # 2️⃣ RESULT / PASS / FAIL
        # =========================
        if "result" in q or "pass" in q or "fail" in q:

            # 🎓 STUDENT → own result
            if role == "student":
                cursor.execute("""
                    SELECT semester, year, marks,
                           CASE WHEN marks >= 40 THEN 'PASS'
                                ELSE 'FAIL' END AS result
                    FROM marks
                    WHERE student_id = %s
                    ORDER BY year DESC, semester DESC
                    LIMIT 1
                """, (student_id,))

                row = cursor.fetchone()
                if not row:
                    return "Result data not available."

                return (
                    f"📄 Latest Result\n"
                    f"Semester: {row['semester']}\n"
                    f"Year: {row['year']}\n"
                    f"Marks: {row['marks']}\n"
                    f"Status: {row['result']}"
                )

            # 👨‍🏫 FACULTY / 👑 ADMIN → recent results
            else:
                cursor.execute("""
                    SELECT s.name, m.marks,
                           CASE WHEN m.marks >= 40 THEN 'PASS'
                                ELSE 'FAIL' END AS result
                    FROM marks m
                    JOIN students s ON m.student_id = s.student_id
                    ORDER BY m.year DESC
                    LIMIT 5
                """)

                rows = cursor.fetchall()
                if not rows:
                    return "Result data not available."

                return "📊 Recent Results:\n" + "\n".join(
                    [f"{r['name']} → {r['marks']} ({r['result']})"
                     for r in rows]
                )

        # =========================
        # 3️⃣ MARKS / PERFORMANCE
        # =========================
        if "mark" in q or "score" in q or "performance" in q:

            # 🎓 STUDENT → own performance
            if role == "student":
                cursor.execute("""
                    SELECT semester, year, marks
                    FROM marks
                    WHERE student_id = %s
                    ORDER BY year DESC, semester DESC
                    LIMIT 3
                """, (student_id,))

                rows = cursor.fetchall()
                if not rows:
                    return "Marks data not available."

                return "📘 Your Recent Marks:\n" + "\n".join(
                    [f"Sem {r['semester']} ({r['year']}) → {r['marks']}"
                     for r in rows]
                )

            # 👨‍🏫 FACULTY / 👑 ADMIN → toppers
            else:
                cursor.execute("""
                    SELECT s.name, AVG(m.marks) AS avg_marks
                    FROM marks m
                    JOIN students s ON m.student_id = s.student_id
                    GROUP BY s.student_id
                    ORDER BY avg_marks DESC
                    LIMIT 5
                """)

                rows = cursor.fetchall()
                if not rows:
                    return "Marks data not available."

                return "🏆 Top Performers:\n" + "\n".join(
                    [f"{r['name']} → Avg {round(r['avg_marks'],2)}"
                     for r in rows]
                )

        return None

    except Exception as e:
        return "⚠️ Unable to retrieve academic data right now."

    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
