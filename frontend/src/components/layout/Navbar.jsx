import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Layers, Box, History, HelpCircle, LogOut, LogIn, Plus } from 'lucide-react';
import useAuthStore from '../../store/authStore';
import Button from '../common/Button';

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: <Layers className="w-4 h-4" />, protected: true },
    { name: 'Design Studio', path: '/studio', icon: <Sparkles className="w-4 h-4" />, protected: true },
    { name: '3D Viewer', path: '/viewer', icon: <Box className="w-4 h-4" />, protected: true },
    { name: 'History', path: '/history', icon: <History className="w-4 h-4" />, protected: true },
    { name: 'How It Works', path: '/help', icon: <HelpCircle className="w-4 h-4" />, protected: false },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-dark-900/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-cyan-400 flex items-center justify-center shadow-glow/50 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            DesignVerse<span className="text-brand-400 ml-0.5">AI</span>
          </span>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks
            .filter((link) => !link.protected || isAuthenticated)
            .map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-slate-800 text-brand-300 font-semibold border border-slate-700/60'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  {link.icon}
                  {link.name}
                </Link>
              );
            })}
        </nav>

        {/* Right Action / Auth */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <Link to="/studio">
                <Button size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                  New Design
                </Button>
              </Link>

              <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
                <Link
                  to="/profile"
                  className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
                  title="Profile"
                >
                  <div className="w-8 h-8 rounded-full bg-brand-600/30 border border-brand-500/40 flex items-center justify-center text-xs font-bold text-brand-300">
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="text-sm font-medium text-slate-300 hidden lg:inline-block">
                    {user?.username || 'User'}
                  </span>
                </Link>

                <button
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-red-400 p-2 rounded-lg hover:bg-slate-800/80 transition-colors cursor-pointer"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/auth">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link to="/auth?tab=register">
                <Button size="sm" leftIcon={<LogIn className="w-4 h-4" />}>
                  Get Started
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
