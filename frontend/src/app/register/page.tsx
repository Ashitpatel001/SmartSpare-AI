import Link from "next/link";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-cyan-50 to-blue-50">
      
      {/* Platform Branding */}
      <div className="mb-8 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-white shadow-sm mb-4">
          <svg className="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-slate-800">
          SmartSpare <span className="text-teal-500">AI</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">Industrial Intelligence Platform</p>
      </div>

      {/* Registration Card */}
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
        <div className="flex items-center gap-2 mb-6">
          <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          <h2 className="text-lg font-semibold text-slate-800">Create Account</h2>
        </div>

        <form className="space-y-4">
          {/* Full Name Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Full Name
            </label>
            <div className="relative">
              <input 
                type="text" 
                placeholder="John Doe" 
                className="w-full px-4 py-3 pl-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all text-sm" 
              />
              <svg className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>

          {/* Email Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Work Email
            </label>
            <div className="relative">
              <input 
                type="email" 
                placeholder="engineer@factory.com" 
                className="w-full px-4 py-3 pl-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all text-sm" 
              />
              <svg className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <input 
                type="password" 
                placeholder="••••••••" 
                className="w-full px-4 py-3 pl-10 rounded-lg bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all text-sm" 
              />
              <svg className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>

          {/* Submit Button */}
          <button 
            type="submit" 
            className="w-full bg-[#5A6373] hover:bg-[#474F5C] text-white font-medium py-3 rounded-lg transition-colors mt-4 text-sm"
          >
            Create Account
          </button>
        </form>

        {/* Router Link back to Login */}
        <div className="mt-6 text-center text-sm text-slate-500 border-t border-slate-100 pt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-teal-600 hover:text-teal-700 font-semibold hover:underline">
            Sign In here
          </Link>
        </div>
      </div>
      
      <div className="mt-8 text-xs text-slate-400">
        Authorized personnel only. All access is logged.
      </div>
    </div>
  );
}