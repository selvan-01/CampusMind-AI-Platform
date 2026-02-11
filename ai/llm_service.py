import ollama

def ask_llm(prompt):
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": "You are CampusMind AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]
