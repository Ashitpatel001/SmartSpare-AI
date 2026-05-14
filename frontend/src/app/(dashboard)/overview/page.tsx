"use client";

import { useQuery } from "@tanstack/react-query";
import { Box, AlertTriangle, FileText, Activity, Bot, Zap, Loader2 } from "lucide-react";
import { getOverviewStats } from "@/services/overview.service";

export default function OverviewPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["overview"],
    queryFn: getOverviewStats,
    refetchInterval: 10000, // Poll every 10 seconds for real-time updates
    staleTime: 0,
  });

  const stats = data || {
    total_parts: 0,
    critical_shortages: 0,
    pending_pos: 0,
    agent_status: "Loading...",
    recent_activity: []
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Personalized Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Welcome back.</h1>
          <p className="text-slate-500 mt-1 font-medium">Here is the real-time cognitive overview of your facility.</p>
        </div>
        <div className="flex items-center gap-2 bg-teal-50 text-teal-700 px-4 py-2 rounded-full border border-teal-100 text-sm font-semibold shadow-sm">
          {isLoading ? <Loader2 size={16} className="animate-spin text-teal-500" /> : <Zap size={16} className="text-teal-500" />}
          System Optimal
        </div>
      </div>

      {/* Live KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Spare Parts" value={stats.total_parts} trend="Live from DB" icon={<Box size={24} className="text-blue-500" />} />
        <StatCard title="Critical Shortages" value={stats.critical_shortages} trend="Requires attention" alert={stats.critical_shortages > 0} icon={<AlertTriangle size={24} className="text-rose-500" />} />
        <StatCard title="Pending POs" value={stats.pending_pos} trend="Awaiting approval" icon={<FileText size={24} className="text-indigo-500" />} />
        <StatCard title="Agent Status" value={stats.agent_status} trend="0 active tasks" icon={<Activity size={24} className="text-teal-500" />} />
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div className="col-span-1 lg:col-span-2 bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
          <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
            <Activity size={20} className="text-slate-400" /> Recent System Activity
          </h2>
          <div className="space-y-4">
            {isLoading && (
              <div className="flex items-center text-slate-400 py-4">
                <Loader2 className="animate-spin mr-2" size={18} /> Loading activity...
              </div>
            )}
            {!isLoading && stats.recent_activity.length === 0 && (
              <p className="text-slate-500 font-medium py-4">No recent activity found.</p>
            )}
            {!isLoading && stats.recent_activity.map((txn: any) => (
              <FeedItem 
                key={txn.id}
                time={new Date(txn.timestamp).toLocaleString()} 
                message={`${txn.action} for '${txn.part_name}' (Qty: ${txn.quantity}) - Status: ${txn.status}`} 
                type={txn.action === "PO_DRAFT" ? "ai" : "system"} 
              />
            ))}
          </div>
        </div>

        <div className="col-span-1 bg-gradient-to-b from-teal-50 to-white border border-teal-100 shadow-sm rounded-2xl p-6 relative overflow-hidden">
          <h2 className="text-lg font-bold text-teal-800 mb-4 relative z-10 flex items-center gap-2">
            <Bot size={20} className="text-teal-600" /> Copilot Suggestions
          </h2>
          <div className="space-y-3 relative z-10">
            {stats.critical_shortages > 0 ? (
              <button className="w-full text-left px-4 py-3 rounded-xl bg-white border border-rose-200 hover:border-rose-400 hover:shadow-md transition-all text-sm font-bold text-rose-700 shadow-sm">
                Review {stats.critical_shortages} critical part shortages
              </button>
            ) : (
              <button className="w-full text-left px-4 py-3 rounded-xl bg-white border border-slate-100 hover:border-teal-300 hover:shadow-md transition-all text-sm font-medium text-slate-700 shadow-sm">
                Inventory levels look good
              </button>
            )}
            {stats.pending_pos > 0 && (
              <button className="w-full text-left px-4 py-3 rounded-xl bg-white border border-amber-200 hover:border-amber-400 hover:shadow-md transition-all text-sm font-bold text-amber-700 shadow-sm">
                Approve {stats.pending_pos} pending POs
              </button>
            )}
            <button className="w-full text-left px-4 py-3 rounded-xl bg-white border border-slate-100 hover:border-teal-300 hover:shadow-md transition-all text-sm font-medium text-slate-700 shadow-sm">
              Analyze recent Error Code E-404
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, trend, icon, alert = false }: any) {
  return (
    <div className={`p-6 rounded-2xl border ${alert ? 'border-rose-200 bg-rose-50/50 shadow-rose-100/50' : 'border-slate-100 bg-white'} shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow`}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-semibold text-slate-500">{title}</h3>
        <div className={`p-2.5 rounded-xl ${alert ? 'bg-rose-100' : 'bg-slate-50'}`}>{icon}</div>
      </div>
      <div>
        <p className={`text-4xl font-extrabold tracking-tight ${alert ? 'text-rose-600' : 'text-slate-800'}`}>{value}</p>
        <p className={`text-sm mt-2 font-medium ${alert ? 'text-rose-500' : 'text-slate-500'}`}>{trend}</p>
      </div>
    </div>
  );
}

function FeedItem({ time, message, type }: any) {
  return (
    <div className="flex gap-4 p-4 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
      <div className="mt-0.5">
        {type === 'ai' && <div className="p-2 bg-teal-100 rounded-lg"><Bot size={16} className="text-teal-600" /></div>}
        {type === 'system' && <div className="p-2 bg-blue-100 rounded-lg"><Activity size={16} className="text-blue-600" /></div>}
        {type === 'user' && <div className="p-2 bg-slate-200 rounded-lg"><FileText size={16} className="text-slate-600" /></div>}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-700">{message}</p>
        <p className="text-xs font-semibold text-slate-400 mt-1">{time}</p>
      </div>
    </div>
  );
}