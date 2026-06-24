import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const API_URL = "http://localhost:8000/chat";
const STORAGE_KEY = "raghav_ai_chat_history";

const QUICK_QUESTIONS = [
  { label: "Who is Raghavendra?", icon: "👤" },
  { label: "Current projects", icon: "🚀" },
  { label: "Tech skills & stack", icon: "⚡" },
  { label: "Work experience", icon: "💼" },
  { label: "Achievements", icon: "🏆" },
  { label: "Contact info", icon: "📬" },
];

const WELCOME = {
  id: "welcome",
  role: "bot",
  text: "Hey there! I'm **Raghavendra's AI assistant**. Ask me anything about his background, projects, skills, certifications, or what he's currently working on. I'm here to help! 👋",
  time: new Date().toISOString(),
};

function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [WELCOME];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed) || parsed.length === 0) return [WELCOME];
    // Filter out any stuck typing bubbles from previous sessions
    return parsed.filter((m) => !m.typing);
  } catch {
    return [WELCOME];
  }
}

function saveHistory(messages) {
  try {
    const toSave = messages.filter((m) => !m.typing);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch {
    // Quota exceeded — fail silently
  }
}

function TypingDots() {
  return (
    <div className="typing-dots">
      <span /><span /><span />
    </div>
  );
}

function BotAvatar() {
  return <div className="avatar bot-av">R</div>;
}

function UserAvatar() {
  return <div className="avatar user-av">U</div>;
}

function ChatMessage({ msg }) {
  const isBot = msg.role === "bot";
  const time = msg.time ? new Date(msg.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";
  return (
    <div className={`msg-row ${isBot ? "bot-row" : "user-row"}`}>
      {isBot && <BotAvatar />}
      <div className={`bubble ${isBot ? "bot-bubble" : "user-bubble"}`}>
        {msg.typing ? (
          <TypingDots />
        ) : isBot ? (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p className="md-p">{children}</p>,
              strong: ({ children }) => <strong className="md-strong">{children}</strong>,
              ol: ({ children }) => <ol className="md-ol">{children}</ol>,
              ul: ({ children }) => <ul className="md-ul">{children}</ul>,
              li: ({ children }) => <li className="md-li">{children}</li>,
              code: ({ node, inline, className, children, ...props }) =>
                inline ? (
                  <code className="md-code-inline" {...props}>{children}</code>
                ) : (
                  <pre className="md-pre"><code className={className} {...props}>{children}</code></pre>
                ),
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" className="md-link">{children}</a>
              ),
            }}
          >
            {msg.text}
          </ReactMarkdown>
        ) : (
          <span>{msg.text}</span>
        )}
        {!msg.typing && (
          <span className="msg-time">{time}</span>
        )}
      </div>
      {!isBot && <UserAvatar />}
    </div>
  );
}

function ClearIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
    </svg>
  );
}

export default function App() {
  const [messages, setMessages] = useState(() => loadHistory());
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const msgsRef = useRef(null);
  const inputRef = useRef(null);

  const scrollBottom = useCallback(() => {
    setTimeout(() => {
      if (msgsRef.current) {
        msgsRef.current.scrollTo({ top: msgsRef.current.scrollHeight, behavior: "smooth" });
      }
    }, 50);
  }, []);

  // Persist to localStorage whenever messages change
  useEffect(() => {
    saveHistory(messages);
  }, [messages]);

  useEffect(scrollBottom, [messages, scrollBottom]);

  const sendMessage = useCallback(async (text) => {
    const question = text.trim();
    if (!question || busy) return;

    setBusy(true);
    setShowClearConfirm(false);

    const userMsg = { id: `u-${Date.now()}`, role: "user", text: question, time: new Date().toISOString() };
    const typingId = `typing-${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: typingId, role: "bot", typing: true, time: new Date().toISOString() },
    ]);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error(`Server responded with ${res.status}`);

      const data = await res.json();
      const answer =
        data.answer.answer || data.response || data.reply || data.message ||
        "Sorry, I couldn't understand the response format.";

      setMessages((prev) =>
        prev.map((m) =>
          m.id === typingId
            ? { id: `b-${Date.now()}`, role: "bot", text: answer, time: new Date().toISOString() }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === typingId
            ? {
                id: `err-${Date.now()}`,
                role: "bot",
                text: `⚠️ Couldn't reach the server. Make sure your FastAPI is running at \`${API_URL}\`.\n\n**Error:** ${err.message}`,
                time: new Date().toISOString(),
              }
            : m
        )
      );
    } finally {
      setBusy(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [busy]);

  const handleSend = () => {
    sendMessage(input);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearHistory = () => {
    if (!showClearConfirm) {
      setShowClearConfirm(true);
      return;
    }
    localStorage.removeItem(STORAGE_KEY);
    setMessages([WELCOME]);
    setShowClearConfirm(false);
  };

  return (
    <div className="app-root">
      <div className="particles">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDuration: `${10 + Math.random() * 10}s`,
            animationDelay: `${Math.random() * -15}s`,
            width: `${2 + Math.random() * 4}px`,
            height: `${2 + Math.random() * 4}px`,
            opacity: 0.3 + Math.random() * 0.3,
          }} />
        ))}
      </div>

      <div className="chat-shell">
        {/* Header */}
        <header className="chat-header">
          <div className="header-avatar">
            <span>R</span>
            <div className="online-dot" />
          </div>
          <div className="header-info">
            <h1>Raghavendra<span className="header-ai">.ai</span></h1>
            <p>Personal Portfolio Assistant</p>
          </div>
          <div className="header-actions">
            <button
              className={`clear-btn ${showClearConfirm ? "confirm" : ""}`}
              onClick={handleClearHistory}
              title={showClearConfirm ? "Click again to confirm" : "Clear chat history"}
            >
              <ClearIcon />
              {showClearConfirm ? "Confirm clear?" : "Clear"}
            </button>
            <div className="header-badge">
              <span className="pulse-dot" />
              Live
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-area" ref={msgsRef}>
          {messages.map((msg) => (
            <ChatMessage key={msg.id} msg={msg} />
          ))}
        </div>

        {/* Quick chips */}
        <div className="chips-bar">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q.label}
              className="chip"
              onClick={() => { sendMessage(q.label); setShowClearConfirm(false); }}
              disabled={busy}
            >
              <span>{q.icon}</span>
              {q.label}
            </button>
          ))}
        </div>

        {/* Input row */}
        <div className="input-row">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about Raghavendra…"
            rows={1}
            disabled={busy}
          />
          <button
            className={`send-btn ${busy ? "loading" : ""}`}
            onClick={handleSend}
            disabled={busy || !input.trim()}
            aria-label="Send message"
          >
            {busy ? (
              <svg viewBox="0 0 24 24" className="spin-icon">
                <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="2.5" strokeDasharray="28 56" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>

        <div className="footer-hint">
          Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line · Chat history is saved automatically
        </div>
      </div>
    </div>
  );
}
