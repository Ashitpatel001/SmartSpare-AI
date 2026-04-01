import { ShoppingCart, CheckCircle2, XCircle, Clock } from "lucide-react";

export default function ProcurementPage() {
  // In a real scenario, you would fetch from a /api/procurement/pending endpoint.
  // We are building the visual shell here to demonstrate the Human-in-the-loop flow.
  
  const pendingOrders = [
    { id: "PO-2026-089", part: "5HP AC Inductive Motor", qty: 10, urgency: "Critical", aiDrafted: true, status: "Pending Approval", cost: "$4,500.00" },
    { id: "PO-2026-090", part: "Hydraulic Pump Seal Kit", qty: 25, urgency: "Normal", aiDrafted: true, status: "Pending Approval", cost: "$850.00" },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100 tracking-tight flex items-center gap-3">
          <ShoppingCart className="text-purple-400" size={32} /> Procurement Console
        </h1>
        <p className="text-slate-400 mt-1">Review and approve Purchase Orders drafted by the Autonomous Agent.</p>
      </div>

      {/* Human-in-the-loop Approval Queue */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-200 border-b border-slate-800/60 pb-2">
          Action Required: Pending Approvals
        </h2>
        
        <div className="grid gap-4">
          {pendingOrders.map((order) => (
            <div key={order.id} className="p-5 rounded-xl border border-slate-800/60 bg-slate-900/40 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-slate-700 transition-colors">
              
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-slate-500 bg-slate-950 px-2 py-1 rounded">{order.id}</span>
                  {order.aiDrafted && (
                    <span className="text-[10px] uppercase tracking-wider font-bold text-teal-400 bg-teal-500/10 border border-teal-500/20 px-2 py-0.5 rounded-full">
                      AI Generated
                    </span>
                  )}
                  {order.urgency === "Critical" && (
                    <span className="text-[10px] uppercase tracking-wider font-bold text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded-full">
                      Urgent
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-medium text-slate-100">{order.part}</h3>
                <p className="text-sm text-slate-400">Requesting <span className="text-slate-200 font-semibold">{order.qty} units</span> at estimated {order.cost}</p>
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto mt-2 md:mt-0">
                <div className="flex items-center gap-2 text-amber-400 text-sm font-medium mr-4">
                  <Clock size={16} /> Awaiting Signoff
                </div>
                <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-300 border border-slate-700 hover:border-red-500/30 rounded-lg transition-colors text-sm font-medium">
                  <XCircle size={16} /> Reject
                </button>
                <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 rounded-lg transition-colors text-sm font-semibold shadow-[0_0_15px_rgba(20,184,166,0.2)]">
                  <CheckCircle2 size={16} /> Approve PO
                </button>
              </div>

            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
