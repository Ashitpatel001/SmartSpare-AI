"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, Filter, Box, Loader2, Plus, Trash2, Edit2, X, UploadCloud, Sparkles } from "lucide-react";
import { useState, useRef } from "react";
import { getInventory, createPart, updatePart, deletePart, uploadInventoryPdf, SparePart } from "@/services/inventory.service";

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<Partial<SparePart>>({
    name: "", sku: "", current_stock: 0, minimum_threshold: 5, location_bin: ""
  });

  const { data, isLoading, isError } = useQuery({ queryKey: ["inventory"], queryFn: getInventory });
  const parts = Array.isArray(data) ? data : [];
  const filteredParts = parts.filter((part: any) => 
    part.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (part.sku && part.sku.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // --- CRUD Mutations ---
  const createMutation = useMutation({
    mutationFn: createPart,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["inventory"] }); closeModal(); }
  });

  const updateMutation = useMutation({
    mutationFn: updatePart,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["inventory"] }); closeModal(); }
  });

  const deleteMutation = useMutation({
    mutationFn: deletePart,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inventory"] })
  });

  // --- AI PDF Upload Mutation ---
  const uploadPdfMutation = useMutation({
    mutationFn: uploadInventoryPdf,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      alert(`Success! ${data.message}`); // Simple success feedback
    },
    onError: (error: any) => {
      alert(`AI Extraction Failed: ${error.response?.data?.detail || error.message}`);
    }
  });

  // --- Handlers ---
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== "application/pdf") {
        alert("Please upload a valid PDF document.");
        return;
      }
      uploadPdfMutation.mutate(file);
    }
    // Reset input so the same file can be selected again if needed
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const openModal = (part?: SparePart) => {
    if (part) {
      setEditingId(part.id);
      setFormData({ name: part.name, sku: part.sku, current_stock: part.current_stock, minimum_threshold: part.minimum_threshold, location_bin: part.location_bin });
    } else {
      setEditingId(null);
      setFormData({ name: "", sku: "", current_stock: 0, minimum_threshold: 5, location_bin: "" });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const sanitizedData = {
      ...formData,
      sku: formData.sku?.trim() === "" ? null : formData.sku,
      location_bin: formData.location_bin?.trim() === "" ? null : formData.location_bin,
      category: null 
    };

    if (editingId) updateMutation.mutate({ id: editingId, data: sanitizedData });
    else createMutation.mutate(sanitizedData);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500 h-full flex flex-col relative">
      
      {/* AI Processing Overlay */}
      {uploadPdfMutation.isPending && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-2xl">
          <div className="flex flex-col items-center p-8 bg-white border border-teal-100 shadow-xl rounded-2xl animate-in zoom-in-95">
            <Sparkles className="text-teal-500 animate-pulse mb-4" size={40} />
            <h2 className="text-xl font-bold text-slate-800">AI is analyzing document...</h2>
            <p className="text-slate-500 font-medium mt-2">Llama 3 is extracting inventory data. This takes a few seconds.</p>
          </div>
        </div>
      )}

      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
            <Box className="text-blue-500" size={32} /> Live Inventory
          </h1>
          <p className="text-slate-500 mt-1 font-medium">Manage stock or let AI digitize your manifests.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search parts..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 w-64 shadow-sm"
            />
          </div>
          
          {/* Hidden File Input */}
          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
          
          {/* AI Upload Button */}
          <button 
            onClick={() => fileInputRef.current?.click()} 
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50 text-indigo-600 rounded-xl text-sm font-bold shadow-sm transition-all"
          >
            <UploadCloud size={18} /> AI PDF Import
          </button>

          {/* Manual Add Button */}
          <button onClick={() => openModal()} className="flex items-center gap-2 px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-sm font-bold shadow-sm transition-colors">
            <Plus size={18} /> Add Part
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="flex-1 border border-slate-200 rounded-2xl overflow-hidden bg-white shadow-sm flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-4 font-bold uppercase tracking-wider text-xs">Part Name</th>
                <th className="px-6 py-4 font-bold uppercase tracking-wider text-xs">SKU</th>
                <th className="px-6 py-4 font-bold uppercase tracking-wider text-xs">Status</th>
                <th className="px-6 py-4 font-bold uppercase tracking-wider text-xs">Stock Level</th>
                <th className="px-6 py-4 font-bold uppercase tracking-wider text-xs text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading && <tr><td colSpan={5} className="px-6 py-16 text-center text-slate-400 font-medium"><Loader2 className="animate-spin text-teal-500 mx-auto mb-2" size={36} /> Loading database...</td></tr>}
              {!isLoading && filteredParts.map((part: any) => {
                const isCritical = part.current_stock === 0;
                return (
                  <tr key={part.id} className="hover:bg-slate-50 transition-colors group">
                    <td className="px-6 py-5 font-bold text-slate-800">{part.name}</td>
                    <td className="px-6 py-5 font-mono text-xs font-semibold text-slate-400">{part.sku || "PENDING"}</td>
                    <td className="px-6 py-5">
                      {isCritical ? <span className="text-rose-700 text-xs font-bold bg-rose-100 px-3 py-1.5 rounded-lg border border-rose-200">OUT OF STOCK</span> : <span className="text-emerald-700 text-xs font-bold bg-emerald-100 px-3 py-1.5 rounded-lg border border-emerald-200">HEALTHY</span>}
                    </td>
                    <td className="px-6 py-5"><span className="text-lg font-extrabold text-slate-800">{part.current_stock}</span></td>
                    <td className="px-6 py-5 text-right space-x-2">
                      <button onClick={() => openModal(part)} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"><Edit2 size={18} /></button>
                      <button onClick={() => deleteMutation.mutate(part.id)} className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"><Trash2 size={18} /></button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual CRUD Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h2 className="text-lg font-bold text-slate-800">{editingId ? "Edit Part" : "Add New Part"}</h2>
              <button onClick={closeModal} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Part Name</label>
                <input required type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">SKU</label>
                  <input type="text" value={formData.sku || ""} onChange={e => setFormData({...formData, sku: e.target.value})} className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Stock Qty</label>
                  <input required type="number" value={formData.current_stock} onChange={e => setFormData({...formData, current_stock: e.target.value === "" ? 0 : parseInt(e.target.value, 10)})} className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100" />
                </div>
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={closeModal} className="px-4 py-2.5 text-slate-600 font-bold hover:bg-slate-100 rounded-xl transition-colors">Cancel</button>
                <button type="submit" disabled={createMutation.isPending || updateMutation.isPending} className="px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl shadow-sm transition-colors disabled:opacity-50">
                  {editingId ? "Save Changes" : "Create Part"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}