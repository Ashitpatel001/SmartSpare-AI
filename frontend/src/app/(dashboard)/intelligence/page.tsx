import { Bot } from "lucide-react";
import ChatInterface from "@/components/ai/chatinterface";

export default function IntelligencePage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6 h-full flex flex-col animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-slate-100 tracking-tight flex items-center gap-3">
          <Bot className="text-teal-400" size={32} /> 
          Autonomous AI Copilot
        </h1>
        <p className="text-slate-400 mt-1">Multi-agent cognitive architecture powered by Llama 3.</p>
      </div>

      <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
        <ChatInterface />
      </div>
    </div>
  );
}