import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MeshGradient from '../components/MeshGradient';
import FloatingParticles from '../components/FloatingParticles';
import { Lock, User, Eye, EyeOff, Sparkles, Shield } from 'lucide-react';

export default function ModernLoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isCardFlipped, setIsCardFlipped] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    setIsCardFlipped(true);

    try {
      await login(formData.username, formData.password);
      setTimeout(() => {
        window.location.href = '/';
      }, 500);
    } catch (err: any) {
      setError(err.message || 'Invalid username or password');
      setIsSubmitting(false);
      setIsCardFlipped(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <MeshGradient />
        <div className="relative z-10">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      <MeshGradient />
      <FloatingParticles />

      <div className="relative max-w-md w-full space-y-8 z-10">
        {/* Animated Header */}
        <div className="text-center animate-fade-in-up">
          <div className="relative inline-block">
            <div className="mx-auto h-24 w-24 bg-gradient-to-br from-orange-500 via-white to-green-600 rounded-full flex items-center justify-center border-4 border-white shadow-2xl animate-float">
              <div className="h-16 w-16 bg-gradient-to-br from-blue-800 to-indigo-900 rounded-full flex items-center justify-center shadow-inner">
                <Shield className="text-white w-8 h-8" />
              </div>
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center animate-pulse">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
          </div>
          
          <h2 className="mt-6 text-4xl font-extrabold bg-gradient-to-r from-orange-600 via-blue-600 to-green-600 bg-clip-text text-transparent">
            NewsScope India
          </h2>
          <p className="mt-2 text-gray-600 font-medium">
            360° Government News Monitoring System
          </p>
          <div className="mt-3 flex items-center justify-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Secure PIB Login Portal</span>
          </div>
        </div>

        {/* Login Card */}
        <div className={`transition-all duration-700 ${isCardFlipped ? 'opacity-50 scale-95' : 'opacity-100 scale-100'}`}>
          <div className="glass rounded-2xl shadow-2xl p-8 border border-white/20">
            {!isCardFlipped ? (
              <form className="space-y-6" onSubmit={handleSubmit}>
                {error && (
                  <div className="bg-gradient-to-r from-red-500 to-pink-600 rounded-xl p-4 animate-scale-in">
                    <div className="flex items-center space-x-3">
                      <svg className="h-5 w-5 text-white flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      <p className="text-sm text-white font-medium">{error}</p>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <label htmlFor="username" className="block text-sm font-semibold text-gray-700">
                    Username
                  </label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <User className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                    </div>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      required
                      value={formData.username}
                      onChange={handleChange}
                      className="glass block w-full pl-12 pr-4 py-3 border border-white/30 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-gray-900 placeholder-gray-400"
                      placeholder="Enter your username"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                    Password
                  </label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.password}
                      onChange={handleChange}
                      className="glass block w-full pl-12 pr-12 py-3 border border-white/30 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-gray-900 placeholder-gray-400"
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer"
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 cursor-pointer">
                      Remember me
                    </label>
                  </div>
                  <a href="#" className="text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors">
                    Forgot password?
                  </a>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="group relative w-full flex justify-center items-center space-x-2 py-3 px-4 rounded-xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span className="font-semibold">Signing in...</span>
                    </>
                  ) : (
                    <>
                      <Lock className="w-5 h-5 group-hover:scale-110 transition-transform" />
                      <span className="font-semibold">Sign in to Dashboard</span>
                    </>
                  )}
                </button>

                <div className="glass rounded-xl p-4 border border-blue-200/50">
                  <p className="text-xs text-gray-600 text-center font-medium mb-2">Demo Credentials:</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="glass rounded-lg p-2 border border-white/20">
                      <p className="text-gray-500">Admin</p>
                      <p className="font-mono text-blue-600">admin / admin</p>
                    </div>
                    <div className="glass rounded-lg p-2 border border-white/20">
                      <p className="text-gray-500">PIB Officer</p>
                      <p className="font-mono text-green-600">pib / pib123</p>
                    </div>
                  </div>
                </div>
              </form>
            ) : (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="relative">
                  <div className="w-20 h-20 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Shield className="w-8 h-8 text-blue-600 animate-pulse" />
                  </div>
                </div>
                <p className="mt-6 text-lg font-semibold text-gray-900">Authenticating...</p>
                <p className="mt-2 text-sm text-gray-600">Please wait while we verify your credentials</p>
              </div>
            )}
          </div>
        </div>

        <div className="text-center text-sm text-gray-500 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <p>© 2025 Government of India. All rights reserved.</p>
          <p className="mt-1">Press Information Bureau (PIB)</p>
        </div>
      </div>
    </div>
  );
}
