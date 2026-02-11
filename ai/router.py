from ai.rag_sql import ask_sql
from ai.rag_docs import ask_docs


def route_question(question, user_context):

    role = user_context.get("role")
    student_id = user_context.get("student_id")

    # 1️⃣ Ask SQL (role aware)
    sql_response = ask_sql(question, role, student_id)

    if sql_response:
        return sql_response

    # 2️⃣ Ask PDF docs
    doc_response = ask_docs(question)

    if doc_response:
        return doc_response

    return "I couldn't find relevant information."
