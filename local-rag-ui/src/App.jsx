import React, { useEffect, useMemo, useRef, useState } from "react";

// ✨ Modern, centered, responsive chat UI (single-file React)
// - Clean top nav, generous spacing, and a max-width container so it never hugs the edge
// - Dark mode toggle, k slider, editable API URL, source chips
// - Sticky composer, loading shimmer, smooth scroll-to-bottom
// - Tailwind classes throughout (works fine even without Tailwind, just less styled)

const IconSun = (props) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
  </svg>
);
const IconMoon = (props) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
);
const IconSend = (props) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path d="m22 2-7 20-4-9-9-4 20-7z"/>
  </svg>
);

export default function App() {
  const [apiBase, setApiBase] = useState("http://127.0.0.1:8000");
  const [query, setQuery] = useState("");
  const [k, setK] = useState(3);
  const [model, setModel] = useState("llama3.1:8b-instruct-q4_K_M"); // display only
  const [messages, setMessages] = useState([]); // {role, text, sources?}
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dark, setDark] = useState(() => window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

  const scrollRef = useRef(null);
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const canAsk = useMemo(() => query.trim().length > 0 && !loading, [query, loading]);

  async function ask() {
    const q = query.trim();
    if (!q) return;
    setError("");
    setLoading(true);
    setMessages((m) => [...m, { role: "user", text: q }]);
    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, k }),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", text: data.answer || "(no answer)", sources: data.sources || [] },
      ]);
    } catch (e) {
      setError(e.message || String(e));
      setMessages((m) => [...m, { role: "assistant", text: "Sorry, something went wrong. Check the API." }]);
    } finally {
      setLoading(false);
      setQuery("");
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); }
  }

  return (
    <div className="min-h-screen text-gray-900 dark:text-gray-100 bg-[radial-gradient(1200px_600px_at_10%_-10%,rgba(59,130,246,0.12),transparent),radial-gradient(800px_400px_at_90%_-20%,rgba(99,102,241,0.12),transparent)] dark:bg-[#0b0f17]">
      {/* Top nav */}
      <nav className="sticky top-0 z-10 backdrop-blur bg-white/60 dark:bg-gray-900/40 border-b border-gray-100 dark:border-gray-800">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600" />
            <div>
              <div className="text-lg font-semibold">Local RAG Chat</div>
              <div className="text-[11px] text-gray-500 dark:text-gray-400">Ollama · Chroma · FastAPI</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5">
              <span className="text-xs text-gray-500">k</span>
              <input type="range" min={2} max={6} value={k} onChange={(e)=>setK(Number(e.target.value))} className="accent-blue-600" />
              <span className="text-xs w-6 text-center">{k}</span>
            </div>
            <button onClick={()=>setDark(d=>!d)} className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white/70 dark:bg-gray-900/40 p-2 hover:shadow-sm">
              {dark ? <IconSun/> : <IconMoon/>}
            </button>
          </div>
        </div>
      </nav>

      {/* Main container */}
      <main className="max-w-5xl mx-auto px-6 pt-8 pb-24">
        {/* Settings bar */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="col-span-2 flex items-center gap-2">
            <label className="text-xs text-gray-500 dark:text-gray-400">API</label>
            <input className="w-full text-sm px-3 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 focus:outline-none" value={apiBase} onChange={(e)=>setApiBase(e.target.value)} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">Model</span>
            <span className="text-xs px-2 py-1 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 truncate">{model}</span>
          </div>
        </div>

        {/* Chat card */}
        <section className="rounded-2xl border border-gray-100 dark:border-gray-800 bg-white/90 dark:bg-gray-900/60 shadow-xl">
          <div ref={scrollRef} className="max-h-[62vh] overflow-auto p-6 space-y-5">
            {messages.length === 0 && (
              <div className="text-sm text-gray-600 dark:text-gray-400">Ask about your docs. Try: <span className="font-medium text-gray-800 dark:text-gray-200">“What is Project Alpha?”</span></div>
            )}
            {messages.map((m, i) => (
              <Message key={i} role={m.role} text={m.text} sources={m.sources} />
            ))}
            {loading && <TypingShimmer />}
          </div>

          {/* Composer */}
          <div className="p-4 border-t border-gray-100 dark:border-gray-800">
            <div className="flex items-end gap-2">
              <textarea
                rows={2}
                value={query}
                onChange={(e)=>setQuery(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Type your question and press Enter…"
                className="flex-1 text-sm px-4 py-3 rounded-2xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              <button onClick={ask} disabled={!canAsk} className="h-11 px-5 rounded-xl bg-blue-600 text-white font-medium disabled:opacity-50 hover:shadow-sm flex items-center gap-2">
                <IconSend/> Ask
              </button>
            </div>
            {error && <div className="text-xs text-red-500 mt-2">{error}</div>}
          </div>
        </section>

        <div className="mt-6 text-xs text-gray-500 dark:text-gray-400">Connected to <code>{apiBase}</code>. Ensure FastAPI is running with CORS enabled.</div>
      </main>
    </div>
  );
}

function Message({ role, text, sources }) {
  const isUser = role === "user";
  return (
    <div className={"flex " + (isUser ? "justify-end" : "justify-start") }>
      <div className={(isUser ? "bg-gradient-to-br from-blue-600 to-indigo-600 text-white" : "bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-100 dark:border-gray-700") + " max-w-[80ch] rounded-2xl px-4 py-3 shadow-sm"}>
        <div className="whitespace-pre-wrap text-[15px] leading-relaxed">{text}</div>
        {Array.isArray(sources) && sources.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {sources.map((s, i) => (
              <span key={i} title={s} className="text-xs px-2 py-1 rounded-full bg-white/70 dark:bg-gray-900/60 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 truncate max-w-[22rem]">
                {s}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingShimmer() {
  return (
    <div className="flex justify-start">
      <div className="max-w-[60ch] rounded-2xl px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <div className="animate-pulse space-y-2">
          <div className="h-3 w-40 rounded bg-gray-200 dark:bg-gray-700"/>
          <div className="h-3 w-64 rounded bg-gray-200 dark:bg-gray-700"/>
          <div className="h-3 w-52 rounded bg-gray-200 dark:bg-gray-700"/>
        </div>
      </div>
    </div>
  );
}
