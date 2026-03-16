const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send-btn");

function detectDevice() {
  const ua = navigator.userAgent.toLowerCase();
  if (/iphone|ipad|ipod/.test(ua)) return "iphone";
  if (/android/.test(ua)) return "android";
  return "desktop";
}

const deviceType = detectDevice();

function linkify(text) {
  const escaped = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return escaped.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
  );
}

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  if (role === "assistant") {
    div.innerHTML = linkify(text);
  } else {
    div.textContent = text;
  }
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "message typing";
  div.id = "typing";
  div.textContent = "Typing...";
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById("typing");
  if (el) el.remove();
}

function setLoading(loading) {
  sendBtn.disabled = loading;
  inputEl.disabled = loading;
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  addMessage(text, "user");
  inputEl.value = "";
  setLoading(true);
  showTyping();

  try {
    const res = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: SESSION_ID,
        message: text,
        device_type: deviceType,
      }),
    });

    if (!res.ok) {
      hideTyping();
      const err = await res.json().catch(() => ({}));
      addMessage(err.detail || "Something went wrong. Please try again.", "assistant");
      return;
    }

    hideTyping();

    // Create a streaming message div
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant";
    messagesEl.appendChild(msgDiv);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let fullText = "";
    let currentEvent = "message";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          currentEvent = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          const raw = line.slice(6);
          if (currentEvent === "chunk") {
            try {
              const { text: chunkText } = JSON.parse(raw);
              fullText += chunkText;
              msgDiv.innerHTML = linkify(fullText);
              messagesEl.scrollTop = messagesEl.scrollHeight;
            } catch {}
          } else if (currentEvent === "error") {
            msgDiv.textContent = "Something went wrong. Please try again.";
          }
        }
      }
    }

    // If nothing was streamed, show fallback
    if (!fullText) {
      msgDiv.textContent = "Sorry, I had trouble responding. Please try again.";
    }
  } catch (e) {
    hideTyping();
    addMessage("Connection error. Please check your internet and try again.", "assistant");
  } finally {
    setLoading(false);
    inputEl.focus();
  }
}

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !sendBtn.disabled) sendMessage();
});

// Fetch initial greeting
async function loadGreeting() {
  showTyping();
  try {
    const res = await fetch(`/api/greeting/${SESSION_ID}`);
    hideTyping();
    if (res.ok) {
      const data = await res.json();
      addMessage(data.reply, "assistant");
    }
  } catch {
    hideTyping();
    addMessage("Hi there! Thanks for choosing R&M Plumbing. Would you mind leaving us a quick Google review?", "assistant");
  }
}

loadGreeting();
