"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Sparkles } from "lucide-react";
import { sendChatMessage } from "@/services/agent.service";

interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "agent",
      content: "System online. I am connected to the live PostgreSQL inventory and ChromaDB manuals. How can I assist the factory floor today?"
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const ACTIVE_FACTORY_ID = "c167061b-b702-477c-9be9-244e32e59730";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userMessage.content, ACTIVE_FACTORY_ID);
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "agent",
        content: response.response || "Task completed."
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (error: any) {
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(),
        role: "agent",
        content: `System Error: Check the backend connection.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      
      <div className="bg-teal-50/50 border-b border-slate-100 p-4 flex items-center gap-3">
        <Sparkles className="text-teal-500" size={20} />
        <span className="font-bold text-teal-900">Agentic Action Stream</span>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`flex-shrink-0 h-10 w-10 rounded-xl flex items-center justify-center shadow-sm ${msg.role === "user" ? "bg-slate-800 text-white" : "bg-teal-100 text-teal-700 border border-teal-200"}`}>
              {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${msg.role === "user" ? "bg-slate-800 text-white rounded-tr-none" : "bg-white text-slate-700 border border-slate-100 rounded-tl-none"}`}>
              <p className="whitespace-pre-wrap text-[15px] font-medium leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-4">
            <div className="flex-shrink-0 h-10 w-10 rounded-xl bg-teal-100 text-teal-700 border border-teal-200 flex items-center justify-center shadow-sm">
              <Bot size={20} />
            </div>
            <div className="max-w-[75%] rounded-2xl p-4 bg-white border border-slate-100 rounded-tl-none shadow-sm flex items-center gap-3">
              <Loader2 size={18} className="text-teal-500 animate-spin" />
              <p className="text-[15px] font-medium text-slate-500">Cognitive loop running...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-white border-t border-slate-100">
        <div className="relative flex items-center">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Instruct the autonomous agent..."
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-5 pr-14 py-4 text-[15px] text-slate-800 font-medium placeholder:text-slate-400 focus:outline-none focus:border-teal-400 focus:ring-4 focus:ring-teal-50 resize-none overflow-hidden h-[60px] transition-all"
            rows={1}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="absolute right-3 p-2.5 bg-teal-500 hover:bg-teal-600 text-white rounded-lg disabled:opacity-50 transition-colors shadow-sm"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}