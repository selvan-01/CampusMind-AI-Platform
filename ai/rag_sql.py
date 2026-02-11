import mysql.connector
from config import MYSQL_CONFIG


def ask_sql(question, role, student_id):

    q = question.lower()

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # =============================
        # 🎓 STUDENT (STRICT ACCESS)
        # =============================
        if role == "student":

            if not student_id:
                return "Student identity not linked."

            # Attendance
            if "attendance" in q:
                cursor.execute("""
                    SELECT subject, percentage
                    FROM attendance
                    WHERE student_id = %s
                """, (student_id,))
                rows = cursor.fetchall()

                if not rows:
                    return "No attendance data found."

                return "\n".join(
                    [f"{r['subject']} → {r['percentage']}%" for r in rows]
                )

            # Marks
            if "mark" in q or "result" in q:
                cursor.execute("""
                    SELECT semester, year, marks
                    FROM marks
                    WHERE student_id = %s
                    ORDER BY year DESC, semester DESC
                """, (student_id,))
                rows = cursor.fetchall()

                if not rows:
                    return "No marks data found."

                return "\n".join(
                    [f"Sem {r['semester']} ({r['year']}) → {r['marks']}"
                     for r in rows]
                )

            return "You can only ask about your own academic data."

        # =============================
        # 👨‍🏫 FACULTY / 👑 ADMIN
        # =============================
        else:

            # Low attendance
            if "low attendance" in q:
                cursor.execute("""
                    SELECT s.name, a.percentage
                    FROM attendance a
                    JOIN students s ON s.student_id = a.student_id
                    WHERE a.percentage < 75
                    ORDER BY a.percentage ASC
                """)
                rows = cursor.fetchall()

                if not rows:
                    return "No low attendance students."

                return "Low Attendance Students:\n" + "\n".join(
                    [f"{r['name']} → {r['percentage']}%"
                     for r in rows]
                )

            # Top performers
            if "top" in q or "best" in q:
                cursor.execute("""
                    SELECT s.name, AVG(m.marks) as avg_marks
                    FROM marks m
                    JOIN students s ON s.student_id = m.student_id
                    GROUP BY s.student_id
                    ORDER BY avg_marks DESC
                    LIMIT 5
                """)
                rows = cursor.fetchall()

                if not rows:
                    return "No data found."

                return "Top Students:\n" + "\n".join(
                    [f"{r['name']} → {round(r['avg_marks'],2)}"
                     for r in rows]
                )

            # Department average
            if "average attendance" in q:
                cursor.execute("""
                    SELECT s.department, AVG(a.percentage) as avg_attendance
                    FROM attendance a
                    JOIN students s ON s.student_id = a.student_id
                    GROUP BY s.department
                """)
                rows = cursor.fetchall()

                if not rows:
                    return "No department data found."

                return "\n".join(
                    [f"{r['department']} → {round(r['avg_attendance'],2)}%"
                     for r in rows]
                )

        return None

    except Exception as e:
        return "Database error occurred."

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
