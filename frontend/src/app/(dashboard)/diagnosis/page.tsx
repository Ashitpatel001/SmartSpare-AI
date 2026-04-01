"use client";

import { useState } from "react";
import { Wrench, UploadCloud, Search, AlertTriangle, Bot, Activity, CheckCircle, ChevronRight, Loader2 } from "lucide-react";
import { runAiDiagnosis } from "@/services/agent.service";

export default function DiagnosisPage() {
  const [errorCode, setErrorCode] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!errorCode.trim()) return;
    
    setIsAnalyzing(true);
    setResult(null);
    
    try {
      const response = await runAiDiagnosis(errorCode);
      // FastAPI returns { status: "success", data: { ... } }
      // The Axios service returns response.data, so we set result to the inner 'data' object
      setResult(response.data); 
    } catch (error) {
      console.error("Diagnosis failed", error);
      alert("AI Diagnosis failed. Check backend terminal for errors.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500 h-full flex flex-col">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
            <Wrench className="text-indigo-500" size={32} /> Fault Diagnosis
          </h1>
          <p className="text-slate-500 mt-1 font-medium">Input machine error codes or upload maintenance logs for AI analysis.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        
        {/* Input Section */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
            <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Search size={20} className="text-slate-400" /> Query System
            </h2>
            <form onSubmit={handleAnalyze} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Error Code or Symptom</label>
                <textarea 
                  value={errorCode}
                  onChange={(e) => setErrorCode(e.target.value)}
                  placeholder="e.g., Overheating conveyor motor..."
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 resize-none h-32 transition-all"
                />
              </div>
              <button 
                type="submit" 
                disabled={isAnalyzing || !errorCode.trim()}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-sm transition-colors disabled:opacity-50"
              >
                {isAnalyzing ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><Bot size={18} /> Run AI Diagnosis</>}
              </button>
            </form>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 text-center border-dashed border-2 hover:border-indigo-400 hover:bg-indigo-50 transition-colors cursor-pointer group">
            <UploadCloud size={32} className="mx-auto text-slate-400 group-hover:text-indigo-500 mb-3 transition-colors" />
            <h3 className="text-sm font-bold text-slate-700">Upload Maintenance Log</h3>
            <p className="text-xs font-medium text-slate-500 mt-1">PDF, TXT, or CSV (Max 5MB)</p>
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col overflow-hidden relative">
          
          {/* Empty State */}
          {!isAnalyzing && !result && (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 p-8">
              <Activity size={48} className="mb-4 opacity-20" />
              <p className="text-lg font-bold text-slate-500">Awaiting Diagnostic Input</p>
              <p className="text-sm font-medium mt-1">Provide an error code or symptom to generate a report.</p>
            </div>
          )}

          {/* Analyzing State */}
          {isAnalyzing && (
            <div className="flex-1 flex flex-col items-center justify-center bg-indigo-50/50 p-8">
              <Bot size={48} className="text-indigo-500 animate-bounce mb-4" />
              <h3 className="text-xl font-bold text-slate-800">Llama 3 is analyzing...</h3>
              <p className="text-slate-500 font-medium mt-2">Diagnosing fault and mapping required spare parts.</p>
            </div>
          )}

          {/* Real AI Result State */}
          {result && !isAnalyzing && (
            <div className="flex-1 flex flex-col animate-in fade-in zoom-in-95 duration-300">
              <div className="p-6 border-b border-slate-100 bg-amber-50">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-amber-100 text-amber-600 rounded-xl border border-amber-200">
                    <AlertTriangle size={24} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-amber-900">{result.title}</h2>
                    <p className="text-amber-700 font-medium text-sm mt-1">
                      Confidence Score: {result.confidence} | Match based on {result.source}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 flex-1 bg-slate-50 overflow-y-auto">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Root Cause Analysis</h3>
                <p className="text-slate-700 text-sm font-medium leading-relaxed bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6">
                  {result.root_cause}
                </p>

                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Required Spare Parts</h3>
                <div className="space-y-3">
                  {result.parts && result.parts.map((part: any, idx: number) => (
                    <PartRequirement 
                      key={idx} 
                      name={part.name} 
                      sku={part.sku} 
                      stock={part.stock} 
                      critical={part.critical} 
                    />
                  ))}
                </div>
              </div>

              <div className="p-4 border-t border-slate-100 bg-white flex justify-end">
                <button className="flex items-center gap-2 px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl shadow-sm transition-colors">
                  Draft Purchase Order <ChevronRight size={18} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PartRequirement({ name, sku, stock, critical = false }: { name: string, sku: string, stock: number, critical?: boolean }) {
  return (
    <div className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
      <div className="flex items-center gap-3">
        {critical ? <AlertTriangle size={18} className="text-rose-500" /> : <CheckCircle size={18} className="text-emerald-500" />}
        <div>
          <p className="font-bold text-slate-800 text-sm">{name}</p>
          <p className="font-mono text-xs text-slate-400 font-semibold">{sku}</p>
        </div>
      </div>
      <div className="text-right">
        <p className={`text-sm font-bold ${stock === 0 ? 'text-rose-600' : 'text-slate-700'}`}>{stock} in stock</p>
        {stock === 0 && <span className="text-[10px] font-bold text-rose-500 uppercase tracking-wider bg-rose-50 px-2 py-1 rounded border border-rose-100">Action Required</span>}
      </div>
    </div>
  );
}