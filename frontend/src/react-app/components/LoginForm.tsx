import { useState } from 'react';
import { Shield, User, Lock, Mail, Phone, Eye, EyeOff } from 'lucide-react';

interface LoginFormProps {
  onLogin: (credentials: { username: string; password: string; userType: string }) => void;
  loading?: boolean;
}

export default function LoginForm({ onLogin, loading = false }: LoginFormProps) {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    userType: 'admin'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    const newErrors: { [key: string]: string } = {};
    
    if (!credentials.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!credentials.password) {
      newErrors.password = 'Password is required';
    } else if (credentials.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setErrors({});
    onLogin(credentials);
  };

  const handleInputChange = (field: string, value: string) => {
    setCredentials(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-xl shadow-2xl p-8 border border-gray-100">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <Shield className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Secure Login</h2>
        <p className="text-gray-600 text-sm">Access your dashboard securely</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* User Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Login As
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setCredentials(prev => ({ ...prev, userType: 'admin' }))}
              className={`p-3 border rounded-lg text-sm font-medium transition-all duration-200 ${
                credentials.userType === 'admin'
                  ? 'border-orange-500 bg-orange-50 text-orange-700'
                  : 'border-gray-300 bg-gray-50 text-gray-600 hover:border-gray-400'
              }`}
            >
              <Shield className="w-4 h-4 mx-auto mb-1" />
              Admin
            </button>
            <button
              type="button"
              onClick={() => setCredentials(prev => ({ ...prev, userType: 'pib_officer' }))}
              className={`p-3 border rounded-lg text-sm font-medium transition-all duration-200 ${
                credentials.userType === 'pib_officer'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 bg-gray-50 text-gray-600 hover:border-gray-400'
              }`}
            >
              <User className="w-4 h-4 mx-auto mb-1" />
              PIB Officer
            </button>
          </div>
        </div>

        {/* Username Field */}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
            Username
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              id="username"
              type="text"
              value={credentials.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                errors.username ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Enter your username"
              aria-label="Username"
              aria-describedby={errors.username ? 'username-error' : undefined}
            />
          </div>
          {errors.username && (
            <p id="username-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.username}
            </p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={credentials.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                errors.password ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Enter your password"
              aria-label="Password"
              aria-describedby={errors.password ? 'password-error' : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.password && (
            <p id="password-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.password}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 transform ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl'
          }`}
          aria-label="Sign in to your account"
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Signing In...</span>
            </div>
          ) : (
            'Sign In'
          )}
        </button>

        {/* Additional Links */}
        <div className="space-y-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            className="w-full text-center text-sm text-blue-600 hover:text-blue-800 transition-colors font-medium"
          >
            Forgot Password?
          </button>
          
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
            <button
              type="button"
              className="flex items-center space-x-1 hover:text-gray-800 transition-colors"
            >
              <Mail className="w-4 h-4" />
              <span>Email Support</span>
            </button>
            <span className="text-gray-300">|</span>
            <button
              type="button"
              className="flex items-center space-x-1 hover:text-gray-800 transition-colors"
            >
              <Phone className="w-4 h-4" />
              <span>Call Support</span>
            </button>
          </div>
        </div>
      </form>

      {/* Security Notice */}
      <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-800 text-center">
          🔒 This is a secure government portal. All activities are logged and monitored.
        </p>
      </div>
    </div>
  );
}
