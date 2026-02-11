import pandas as pd
import mysql.connector
from config import MYSQL_CONFIG


# ---------------- STUDENTS (UPSERT) ----------------
def upload_students_excel(file_path):
    df = pd.read_excel(file_path)

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(buffered=True)

    for _, row in df.iterrows():
        sql = """
        INSERT INTO students (student_id, name, department, year, email)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            department = VALUES(department),
            year = VALUES(year),
            email = VALUES(email)
        """
        values = (
            int(row["student_id"]),
            row["name"],
            row["department"],
            int(row["year"]),
            row["email"]
        )
        cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()


# ---------------- ATTENDANCE (UPSERT – NO DUPLICATES) ----------------
def upload_attendance_excel(file_path):
    df = pd.read_excel(file_path)

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(buffered=True)

    for _, row in df.iterrows():
        sql = """
        INSERT INTO attendance (student_id, month, year, percentage)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            month = VALUES(month),
            year = VALUES(year),
            percentage = VALUES(percentage),
            mail_sent = FALSE
        """
        values = (
            int(row["student_id"]),
            row["month"],
            int(row["year"]),
            float(row["percentage"])
        )
        cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()


# ---------------- MARKS (UPSERT – NO DUPLICATES) ----------------
def upload_marks_excel(file_path):
    df = pd.read_excel(file_path)

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(buffered=True)

    for _, row in df.iterrows():
        sql = """
        INSERT INTO marks (student_id, semester, year, marks)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            semester = VALUES(semester),
            year = VALUES(year),
            marks = VALUES(marks)
        """
        values = (
            int(row["student_id"]),
            int(row["semester"]),
            int(row["year"]),
            int(row["marks"])
        )
        cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()
def upload_exam_excel(file_path):
    import pandas as pd
    import mysql.connector
    from config import MYSQL_CONFIG

    df = pd.read_excel(file_path)

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(buffered=True)

    for _, row in df.iterrows():
        sql = """
        INSERT INTO exam_schedule (subject, exam_date, department, year, reminder_sent)
        VALUES (%s, %s, %s, %s, FALSE)
        """
        cursor.execute(sql, (
            row["subject"],
            row["exam_date"],
            row["department"],
            int(row["year"])
        ))

    conn.commit()
    cursor.close()
    conn.close()
