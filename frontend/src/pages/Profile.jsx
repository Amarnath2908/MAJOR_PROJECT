import React from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Calendar, ShieldCheck, LogOut, Layers, Box, Sparkles } from 'lucide-react';
import useAuthStore from '../store/authStore';
import { useUserProfileQuery } from '../queries/useQueries';
import Button from '../components/common/Button';
import { formatDate } from '../utils/formatDate';

export function Profile() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const { data: profile, isLoading } = useUserProfileQuery();
  const current = profile || user;

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="p-6 sm:p-8 max-w-4xl mx-auto w-full space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          User Profile & Settings
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Manage your account credentials and workspace stats.
        </p>
      </div>

      {/* Main Profile Card */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-slate-800">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-brand-600 to-cyan-400 flex items-center justify-center text-xl font-black text-white shadow-glow">
              {current?.username?.charAt(0).toUpperCase() || 'U'}
            </div>

            <div>
              <h2 className="text-xl font-bold text-white">
                {current?.full_name || current?.username || 'Designer'}
              </h2>
              <p className="text-xs text-brand-300 font-mono">@{current?.username}</p>
            </div>
          </div>

          <Button
            variant="danger"
            size="sm"
            onClick={handleLogout}
            leftIcon={<LogOut className="w-4 h-4" />}
          >
            Sign Out
          </Button>
        </div>

        {/* User Details Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
            <Mail className="w-5 h-5 text-slate-500 flex-shrink-0" />
            <div className="min-w-0">
              <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Email Address</span>
              <p className="text-sm font-medium text-white truncate">{current?.email}</p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
            <Calendar className="w-5 h-5 text-slate-500 flex-shrink-0" />
            <div>
              <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Member Since</span>
              <p className="text-sm font-medium text-white">{formatDate(current?.created_at)}</p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <div>
              <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Account Status</span>
              <p className="text-sm font-medium text-emerald-400">Active &bull; Verified JWT Session</p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
            <Layers className="w-5 h-5 text-brand-400 flex-shrink-0" />
            <div>
              <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Total Projects Created</span>
              <p className="text-sm font-medium text-white">{current?.total_projects ?? 0} Designs</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
