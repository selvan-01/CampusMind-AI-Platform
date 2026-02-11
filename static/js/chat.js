function sendMessage() {
  const input = document.getElementById("question");
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById("chatBox");

  // USER MESSAGE
  const userDiv = document.createElement("div");
  userDiv.className = "user-msg";
  userDiv.innerHTML = `<span>${msg}</span>`;
  chatBox.appendChild(userDiv);

  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  // SHOW TYPING
  document.getElementById("typing").style.display = "block";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "question=" + encodeURIComponent(msg),
  })
    .then((res) => res.text())
    .then((reply) => {
      document.getElementById("typing").style.display = "none";

      const aiDiv = document.createElement("div");
      aiDiv.className = "ai-msg";
      aiDiv.innerHTML = `<span>${reply}</span>`;
      chatBox.appendChild(aiDiv);

      chatBox.scrollTop = chatBox.scrollHeight;
    });
}
