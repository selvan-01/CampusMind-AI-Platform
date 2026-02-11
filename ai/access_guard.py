# ai/access_guard.py

def check_access(intent, user_context):
    """
    intent       : detected intent from NLP
    user_context : {
        role: "student" | "faculty" | "admin",
        student_id: int
    }
    """

    role = user_context.get("role")

    # ---------------- STUDENT RULES ----------------
    if role == "student":
        if intent in [
            "OTHER_STUDENT_DATA",
            "DEPARTMENT_ANALYTICS",
            "ALL_RESULTS",
            "ALL_ATTENDANCE"
        ]:
            return False, "❌ You are not allowed to access other students' data."

        return True, None

    # ---------------- FACULTY RULES ----------------
    if role == "faculty":
        return True, None

    # ---------------- ADMIN RULES ----------------
    if role == "admin":
        return True, None

    return False, "❌ Unauthorized access."
def is_allowed(intent, role):
    if role == "student" and intent == "OTHER_STUDENT_DATA":
        return False
    return True
