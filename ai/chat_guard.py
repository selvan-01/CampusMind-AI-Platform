def check_permission(intent, role):
    """
    Returns (allowed: bool, message: str)
    This version NEVER blocks silently.
    """

    # ================= STUDENT RULES =================
    if role == "student":
        if intent == "admin_stats":
            return False, "🚫 Students are not allowed to view admin statistics."

    # ================= FACULTY RULES =================
    if role == "faculty":
        # Faculty can view student data but not admin insights
        if intent == "admin_stats":
            return False, "🚫 Faculty cannot access admin insights."

    # ================= ADMIN RULES =================
    if role == "admin":
        # Admin has full access
        return True, "Allowed"

    # ================= DEFAULT =================
    return True, "Allowed"
