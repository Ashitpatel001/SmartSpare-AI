"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ShoppingCart, CheckCircle2, XCircle, Clock, Loader2, PackageOpen } from "lucide-react";
import { getPendingPOs, approvePO, rejectPO, PurchaseOrder } from "@/services/procurement.service";

export default function ProcurementPage() {
  const queryClient = useQueryClient();

  const { data: pendingOrders = [], isLoading } = useQuery({
    queryKey: ["procurement"],
    queryFn: getPendingPOs,
    refetchInterval: 5000, // Poll every 5 seconds for real-time updates
    staleTime: 0,
  });

  const approveMutation = useMutation({
    mutationFn: approvePO,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["procurement"] }),
  });

  const rejectMutation = useMutation({
    mutationFn: rejectPO,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["procurement"] }),
  });

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
          <ShoppingCart className="text-indigo-500" size={32} /> Procurement Console
        </h1>
        <p className="text-slate-500 mt-1 font-medium">Review and approve Purchase Orders drafted by the AI Agent. All data is live from PostgreSQL.</p>
      </div>

      {/* Human-in-the-loop Approval Queue */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2">
          Action Required: Pending Approvals ({pendingOrders.length})
        </h2>
        
        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-16 text-slate-400">
            <Loader2 className="animate-spin mr-3" size={24} />
            <span className="font-medium">Loading purchase orders from database...</span>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && pendingOrders.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400 bg-white border border-slate-200 rounded-2xl">
            <PackageOpen size={48} className="mb-4 opacity-30" />
            <p className="text-lg font-bold text-slate-500">No Pending Purchase Orders</p>
            <p className="text-sm font-medium mt-1">POs will appear here when the AI Agent drafts them via the Copilot.</p>
          </div>
        )}

        {/* PO Cards */}
        <div className="grid gap-4">
          {pendingOrders.map((order: PurchaseOrder) => (
            <div key={order.id} className="p-5 rounded-2xl border border-slate-200 bg-white flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-slate-300 hover:shadow-sm transition-all shadow-sm">
              
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded-lg border border-slate-200">
                    {order.id.slice(0, 8)}...
                  </span>
                  <span className="text-[10px] uppercase tracking-wider font-bold text-teal-600 bg-teal-50 border border-teal-100 px-2 py-0.5 rounded-full">
                    AI Generated
                  </span>
                  {order.urgency === "critical" && (
                    <span className="text-[10px] uppercase tracking-wider font-bold text-rose-600 bg-rose-50 border border-rose-100 px-2 py-0.5 rounded-full">
                      Urgent
                    </span>
                  )}
                  {order.urgency === "expedited" && (
                    <span className="text-[10px] uppercase tracking-wider font-bold text-amber-600 bg-amber-50 border border-amber-100 px-2 py-0.5 rounded-full">
                      Expedited
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-slate-800">{order.part_name}</h3>
                <p className="text-sm text-slate-500 font-medium">
                  Requesting <span className="text-slate-800 font-bold">{order.quantity} units</span> · SKU: <span className="font-mono text-xs">{order.sku}</span>
                </p>
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto mt-2 md:mt-0">
                <div className="flex items-center gap-2 text-amber-500 text-sm font-semibold mr-4">
                  <Clock size={16} /> Awaiting Signoff
                </div>
                <button 
                  onClick={() => rejectMutation.mutate(order.id)}
                  disabled={rejectMutation.isPending}
                  className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-white hover:bg-rose-50 text-slate-600 hover:text-rose-600 border border-slate-200 hover:border-rose-200 rounded-xl transition-colors text-sm font-bold disabled:opacity-50"
                >
                  <XCircle size={16} /> Reject
                </button>
                <button 
                  onClick={() => approveMutation.mutate(order.id)}
                  disabled={approveMutation.isPending}
                  className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl transition-colors text-sm font-bold shadow-sm disabled:opacity-50"
                >
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
