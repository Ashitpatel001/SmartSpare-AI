"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Box, Wrench, ShoppingCart, Bot, Settings, Bell, Factory } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-50 text-slate-900">
      
      {/* Primary Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-200 bg-white flex flex-col hidden md:flex shadow-sm z-20">
        <div className="h-16 flex items-center px-6 border-b border-slate-100">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <Bot className="text-teal-600" size={24} />
            <span className="text-slate-800">SmartSpare</span>
            <span className="text-teal-600">AI</span>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 mt-4">Command Center</p>
          <NavItem href="/overview" icon={<Activity size={18} />} label="Overview" active={pathname === "/overview"} />
          <NavItem href="/inventory" icon={<Box size={18} />} label="Live Inventory" active={pathname === "/inventory"} />
          
          <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 mt-6">Intelligence</p>
          <NavItem href="/diagnosis" icon={<Wrench size={18} />} label="Fault Diagnosis" active={pathname === "/diagnosis"} />
          <NavItem href="/intelligence" icon={<Bot size={18} />} label="AI Copilot" active={pathname === "/intelligence"} />
          
          <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 mt-6">Operations</p>
          <NavItem href="/procurement" icon={<ShoppingCart size={18} />} label="Procurement" active={pathname === "/procurement"} />
        </nav>

        <div className="p-4 border-t border-slate-100">
          <NavItem href="/settings" icon={<Settings size={18} />} label="Settings" active={pathname === "/settings"} />
        </div>
      </aside>

      {/* Main Content Wrapper */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <header className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-6 z-10 shadow-sm">
          <div className="flex items-center gap-3 text-sm">
            <Factory size={16} className="text-slate-500" />
            <span className="text-slate-500 font-medium">Active Facility:</span>
            <span className="bg-slate-100 border border-slate-200 text-slate-700 px-3 py-1 rounded-full font-mono text-xs font-semibold shadow-sm">
              Apex Industrial Mfg.
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="relative text-slate-400 hover:text-teal-600 transition-colors">
              <Bell size={20} />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-teal-500"></span>
              </span>
            </button>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-teal-400 to-blue-500 border border-slate-200 shadow-sm" />
          </div>
        </header>

        <div className="flex-1 overflow-y-auto bg-slate-50 p-6 relative">
          {children}
        </div>
      </main>
    </div>
  );
}

function NavItem({ href, icon, label, active = false }: { href: string; icon: React.ReactNode; label: string; active?: boolean }) {
  return (
    <Link 
      href={href} 
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
        active 
          ? "bg-teal-50 text-teal-700 font-semibold shadow-sm border border-teal-100" 
          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent"
      }`}
    >
      <span className={`${active ? "text-teal-600" : "text-slate-400 group-hover:text-teal-500 transition-colors"}`}>
        {icon}
      </span>
      {label}
    </Link>
  );
}