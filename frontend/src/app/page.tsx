"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Mail, Lock, Box, ArrowRight, Loader2, ShieldCheck } from "lucide-react";
import { loginUser } from "@/services/auth.service";

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [credentials, setCredentials] = useState({ email: "", password: "" });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // 1. Send credentials to FastAPI via the auth service
      const data = await loginUser(credentials.email, credentials.password);
      
      // 2. Save the cryptographic token securely in the browser
      localStorage.setItem("access_token", data.access_token);
      
      // 3. Redirect to the protected dashboard
      router.push("/inventory"); 
    } catch (error) {
      console.error("Login failed", error);
      alert("Invalid email or password. Access Denied.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 relative overflow-hidden">
      
      {/* Background Decorative Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-teal-400/20 rounded-full blur-3xl" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl" />

      <div className="w-full max-w-md p-8 relative z-10 animate-in fade-in zoom-in-95 duration-500">
        
        {/* Branding Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white shadow-sm border border-slate-100 mb-4">
            <Box className="text-teal-600" size={32} />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">SmartSpare <span className="text-teal-600">AI</span></h1>
          <p className="text-slate-500 font-medium mt-2">Industrial Intelligence Platform</p>
        </div>

        {/* Login Form Card */}
        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-8">
          <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
            <ShieldCheck className="text-indigo-500" size={24} /> Secure Access
          </h2>
          
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Work Email</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input 
                  required 
                  type="email" 
                  placeholder="engineer@factory.com"
                  value={credentials.email}
                  onChange={e => setCredentials({...credentials, email: e.target.value})}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 transition-all"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Password</label>
                <a href="#" className="text-xs font-bold text-teal-600 hover:text-teal-700">Forgot?</a>
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input 
                  required 
                  type="password" 
                  placeholder="••••••••"
                  value={credentials.password}
                  onChange={e => setCredentials({...credentials, password: e.target.value})}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 transition-all"
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading || !credentials.email || !credentials.password}
              className="w-full flex items-center justify-center gap-2 px-6 py-3.5 mt-4 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl shadow-md transition-all disabled:opacity-70"
            >
              {isLoading ? (
                <><Loader2 size={18} className="animate-spin" /> Authenticating...</>
              ) : (
                <>Sign In to Dashboard <ArrowRight size={18} /></>
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-xs font-medium text-slate-400 mt-8">
          Authorized personnel only. All access is logged.
        </p>
      </div>
    </div>
  );
}