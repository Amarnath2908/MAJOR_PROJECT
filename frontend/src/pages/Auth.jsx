import React, { useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Sparkles, Mail, Lock, User as UserIcon, ArrowRight, AlertCircle } from 'lucide-react';
import { loginSchema, registerSchema } from '../schemas/authSchemas';
import authService from '../services/authService';
import useAuthStore from '../store/authStore';
import Input from '../components/common/Input';
import Button from '../components/common/Button';

export function Auth() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') === 'register' ? 'register' : 'login';
  const [activeTab, setActiveTab] = useState(initialTab);
  const [authError, setAuthError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const { setAuth } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const redirectUrl = searchParams.get('redirect') || '/dashboard';

  // Login form
  const loginForm = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  // Register form
  const registerForm = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { username: '', email: '', password: '', confirmPassword: '', full_name: '' },
  });

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setAuthError(null);
    setSearchParams(tab === 'register' ? { tab: 'register' } : {});
  };

  const onLoginSubmit = async (data) => {
    setAuthError(null);
    setIsLoading(true);
    try {
      const response = await authService.login(data);
      setAuth(response);
      navigate(redirectUrl, { replace: true });
    } catch (err) {
      if (err.response?.status === 401) {
        setAuthError('Incorrect email or password. Please check your credentials.');
      } else if (err.response?.data?.detail) {
        setAuthError(err.response.data.detail);
      } else {
        setAuthError('Unable to connect to the server. Please check your backend connection.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const onRegisterSubmit = async (data) => {
    setAuthError(null);
    setIsLoading(true);
    try {
      const response = await authService.register(data);
      setAuth(response);
      navigate(redirectUrl, { replace: true });
    } catch (err) {
      if (err.response?.status === 409) {
        setAuthError('An account with this email or username already exists.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          setAuthError(detail.map((d) => d.msg).join(', '));
        } else {
          setAuthError(detail);
        }
      } else {
        setAuthError('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-md glass-panel p-8 rounded-3xl border border-slate-800/80 shadow-2xl relative">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-400 mx-auto flex items-center justify-center shadow-glow mb-3">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">DesignVerse AI</h2>
          <p className="text-xs text-slate-400 mt-1">
            {activeTab === 'login' ? 'Sign in to access your spaces' : 'Create an account to start designing'}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex p-1 bg-slate-900/90 rounded-xl border border-slate-800 mb-6">
          <button
            type="button"
            onClick={() => handleTabChange('login')}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              activeTab === 'login'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => handleTabChange('register')}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              activeTab === 'register'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {/* Auth Error Banner */}
        {authError && (
          <div className="p-3 bg-red-950/50 border border-red-800/60 rounded-xl flex items-start gap-2.5 text-xs text-red-300 mb-5">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <span>{authError}</span>
          </div>
        )}

        {/* Login Form */}
        {activeTab === 'login' ? (
          <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="you@example.com"
              leftIcon={<Mail className="w-4 h-4" />}
              error={loginForm.formState.errors.email?.message}
              {...loginForm.register('email')}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={loginForm.formState.errors.password?.message}
              {...loginForm.register('password')}
            />

            <Button
              type="submit"
              className="w-full mt-2"
              size="md"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In to DesignVerse
            </Button>
          </form>
        ) : (
          /* Register Form */
          <form onSubmit={registerForm.handleSubmit(onRegisterSubmit)} className="space-y-3.5">
            <Input
              label="Username"
              type="text"
              placeholder="e.g. john_architect"
              leftIcon={<UserIcon className="w-4 h-4" />}
              error={registerForm.formState.errors.username?.message}
              {...registerForm.register('username')}
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="you@example.com"
              leftIcon={<Mail className="w-4 h-4" />}
              error={registerForm.formState.errors.email?.message}
              {...registerForm.register('email')}
            />

            <Input
              label="Full Name (Optional)"
              type="text"
              placeholder="John Doe"
              leftIcon={<UserIcon className="w-4 h-4" />}
              error={registerForm.formState.errors.full_name?.message}
              {...registerForm.register('full_name')}
            />

            <Input
              label="Password (min 8 chars)"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={registerForm.formState.errors.password?.message}
              {...registerForm.register('password')}
            />

            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={registerForm.formState.errors.confirmPassword?.message}
              {...registerForm.register('confirmPassword')}
            />

            <Button
              type="submit"
              className="w-full mt-2"
              size="md"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Create Account
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}

export default Auth;
