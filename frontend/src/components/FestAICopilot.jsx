import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  Bot,
  Send,
  X,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Shield,
  Zap,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Calendar,
  Users,
  Award,
  BarChart3,
  FileCheck,
} from "lucide-react";
import { agentsApi } from "../api/agentsApi";
import { useAuth } from "../auth/AuthContext";

export default function FestAICopilot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "assistant",
      agentName: "Fest Supervisor Agent",
      route: "supervisor",
      text: "👋 Welcome to the **Fest AI Copilot**! Powered by LangGraph multi-agent intelligence. Ask me about event schedules, team rosters, live scoring rubrics, QR passes, or real-time fest analytics.",
      trace: ["Supervisor initialized and listening"],
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [agentStatus, setAgentStatus] = useState(null);
  const [showTraceFor, setShowTraceFor] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const effectiveRole = user?.role ? String(user.role).toLowerCase() : "student";

  useEffect(() => {
    fetchSuggestions();
    fetchStatus();
  }, [user]);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchSuggestions = async () => {
    try {
      const data = await agentsApi.getSuggestions(effectiveRole);
      setSuggestions(data.suggestions || []);
    } catch (_) {
      setSuggestions([
        "What events are scheduled for today?",
        "Check my registration status",
        "What are the rules and team size for Coding?",
      ]);
    }
  };

  const fetchStatus = async () => {
    try {
      const data = await agentsApi.getStatus();
      setAgentStatus(data);
    } catch (_) {}
  };

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query || loading) return;

    const userMessageId = `user-${Date.now()}`;
    const newUserMsg = {
      id: userMessageId,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInput("");
    setLoading(true);

    try {
      const historyTurns = messages
        .slice(-4)
        .map((m) => `${m.sender.toUpperCase()}: ${m.text.substring(0, 120)}`);

      const res = await agentsApi.chat({
        question: query,
        role: effectiveRole,
        event_context: {
          user_id: user?.id,
          user_name: user?.full_name,
          user_role: effectiveRole,
        },
        history: historyTurns,
      });

      const assistantMsg = {
        id: `agent-${Date.now()}`,
        sender: "assistant",
        agentName: res.agent_name || "Specialist Agent",
        route: res.route_taken,
        text: res.response,
        trace: res.trace || [],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error("AI Copilot request error", err);
      const errorMsg = {
        id: `error-${Date.now()}`,
        sender: "assistant",
        agentName: "Fest AI Helpdesk",
        route: "faq_agent",
        text: "⚠️ I encountered a temporary network delay reaching the AI agents. Please try again or rephrase your question.",
        trace: ["Error caught during dispatch"],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: "welcome-reset",
        sender: "assistant",
        agentName: "Fest Supervisor Agent",
        route: "supervisor",
        text: "✨ Conversation reset. How can our specialized fest agents assist you now?",
        trace: ["Session context reset"],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  const renderFormattedText = (text) => {
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      if (line.startsWith("### ")) {
        return (
          <h4 key={idx} className="font-extrabold text-amber-400 text-sm mt-2 mb-1">
            {line.replace("### ", "")}
          </h4>
        );
      }
      if (line.startsWith("## ")) {
        return (
          <h3 key={idx} className="font-black text-amber-300 text-base mt-2 mb-1">
            {line.replace("## ", "")}
          </h3>
        );
      }
      if (line.startsWith("• ") || line.startsWith("- ")) {
        return (
          <li key={idx} className="ml-4 list-disc text-slate-200 text-xs my-0.5 leading-relaxed">
            {line.replace(/^[•-]\s+/, "")}
          </li>
        );
      }
      if (!line.trim()) {
        return <div key={idx} className="h-1.5" />;
      }
      return (
        <p key={idx} className="text-xs text-slate-200 leading-relaxed my-0.5">
          {line}
        </p>
      );
    });
  };

  return (
    <>
      {/* Floating Trigger Button */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          className="group relative flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-2xl shadow-amber-500/30 hover:shadow-amber-500/50 hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer border border-amber-300/40"
          title="Open Fest AI Multi-Agent Copilot"
        >
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-slate-950 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-slate-950"></span>
          </span>
          <Sparkles className="w-4 h-4 text-slate-950 animate-pulse" />
          <span className="tracking-wide uppercase font-black text-[11px]">EVENTX AI </span>
        </button>
      </div>

      {/* Slide-Over Drawer / Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 sm:right-6 z-50 w-[92vw] sm:w-[440px] max-w-[460px] h-[640px] max-h-[85vh] flex flex-col rounded-3xl bg-slate-950/95 border border-amber-500/30 shadow-2xl shadow-black/80 backdrop-blur-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="p-4 bg-slate-900/90 border-b border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-white text-sm tracking-tight">Fest AI Copilot</h3>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-[9px] font-bold text-emerald-400 uppercase tracking-wider">
                    Live
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-amber-400" />
                  LangGraph 7-Agent Network • Role: <span className="font-mono uppercase text-amber-300">{effectiveRole}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleClearChat}
                className="p-1.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                title="Reset conversation"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                title="Close AI Copilot"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Agent Capability Strip */}
          <div className="px-4 py-2 bg-slate-900/40 border-b border-slate-800/50 flex items-center gap-1.5 overflow-x-auto text-[10px] text-slate-400 whitespace-nowrap scrollbar-none">
            <span className="font-bold text-amber-400/90 uppercase tracking-wider text-[9px]">Routing:</span>
            <span className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/40">📅 Events</span>
            <span className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/40">👥 Squads</span>
            <span className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/40">⚖️ Judging</span>
            <span className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/40">🏆 Results</span>
            <span className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/40">📊 Analytics</span>
          </div>

          {/* Message Stream */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => {
              const isUser = msg.sender === "user";
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isUser ? "items-end" : "items-start"} space-y-1`}
                >
                  {/* Agent badge for assistant */}
                  {!isUser && (
                    <div className="flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-bold text-amber-400">
                      <Sparkles className="w-3 h-3 text-amber-400" />
                      <span>{msg.agentName}</span>
                      <span className="text-slate-500 font-normal">• {msg.timestamp}</span>
                    </div>
                  )}

                  {/* Message Bubble */}
                  <div
                    className={`max-w-[88%] p-3.5 rounded-2xl text-xs ${
                      isUser
                        ? "bg-amber-500 text-slate-950 font-medium rounded-br-none shadow-md shadow-amber-500/10"
                        : "bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none shadow-lg"
                    }`}
                  >
                    {isUser ? (
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                    ) : (
                      <div className="space-y-1">{renderFormattedText(msg.text)}</div>
                    )}
                  </div>

                  {/* Trace Toggle for Assistant */}
                  {!isUser && msg.trace && msg.trace.length > 0 && (
                    <div className="text-[10px] text-slate-500 pl-1">
                      <button
                        onClick={() =>
                          setShowTraceFor(showTraceFor === msg.id ? null : msg.id)
                        }
                        className="hover:text-amber-400 transition-colors flex items-center gap-1"
                      >
                        {showTraceFor === msg.id ? (
                          <>
                            <ChevronUp className="w-3 h-3" /> Hide Agent Trace
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-3 h-3" /> View Route Trace ({msg.trace.length} steps)
                          </>
                        )}
                      </button>

                      {showTraceFor === msg.id && (
                        <div className="mt-1.5 p-2 rounded-xl bg-slate-950 border border-slate-800/80 font-mono text-[9px] text-slate-400 space-y-0.5">
                          {msg.trace.map((step, sIdx) => (
                            <div key={sIdx} className="flex items-center gap-1">
                              <span className="text-amber-400">→</span> {step}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex items-start gap-2">
                <div className="w-7 h-7 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 animate-spin">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                  Supervisor routing & generating multi-agent response...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions Chips */}
          {suggestions.length > 0 && (
            <div className="px-3 py-2 bg-slate-900/60 border-t border-slate-800/60">
              <div className="text-[10px] text-slate-400 font-bold mb-1.5 flex items-center gap-1 uppercase tracking-wider">
                <HelpCircle className="w-3 h-3 text-amber-400" /> Suggested for you:
              </div>
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                {suggestions.slice(0, 4).map((sugg, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(sugg)}
                    disabled={loading}
                    className="shrink-0 px-2.5 py-1 rounded-xl bg-slate-800/80 hover:bg-amber-500/15 border border-slate-700/60 hover:border-amber-500/30 text-[11px] text-slate-300 hover:text-amber-300 transition-all text-left"
                  >
                    {sugg}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              placeholder="Ask Fest AI (e.g. schedules, team rules, rubrics)..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              className="flex-1 px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 font-bold transition-all shadow-md shadow-amber-500/20"
              title="Send prompt"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
