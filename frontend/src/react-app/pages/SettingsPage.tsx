import { useState, useEffect } from 'react';
import { useAutoRefresh } from '@/react-app/hooks/useAutoRefresh';
import { Settings, Activity, RefreshCw, CheckCircle, XCircle, Clock, Save, Filter } from 'lucide-react';
import { formatLastUpdated } from '@/react-app/utils/textCleanup';

interface HealthStatus {
  status: string;
  name: string;
  env: string;
}

export default function SettingsPage() {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [defaultLanguage, setDefaultLanguage] = useState('en');
  const [timeRange, setTimeRange] = useState('24h');
  const [showToast, setShowToast] = useState(false);
  const [preferredCategory, setPreferredCategory] = useState('');
  const [preferredRegion, setPreferredRegion] = useState('');
  const [preferredSentiment, setPreferredSentiment] = useState('');
  
  const { data: health, loading, error, refetch, lastUpdated } = useAutoRefresh<HealthStatus>(
    '/health',
    autoRefresh ? 30000 : 0
  );

  useEffect(() => {
    const saved = localStorage.getItem('settings');
    if (saved) {
      const settings = JSON.parse(saved);
      setAutoRefresh(settings.autoRefresh ?? true);
      setDarkMode(settings.darkMode ?? false);
      setDefaultLanguage(settings.defaultLanguage ?? 'en');
      setTimeRange(settings.timeRange ?? '24h');
      setPreferredCategory(settings.preferredCategory ?? '');
      setPreferredRegion(settings.preferredRegion ?? '');
      setPreferredSentiment(settings.preferredSentiment ?? '');
    }
  }, []);

  const saveSettings = (showNotification = false) => {
    const settings = { 
      autoRefresh, 
      darkMode, 
      defaultLanguage, 
      timeRange,
      preferredCategory,
      preferredRegion,
      preferredSentiment
    };
    localStorage.setItem('settings', JSON.stringify(settings));
    if (showNotification) {
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    }
  };

  useEffect(() => {
    saveSettings(false);
  }, [autoRefresh, darkMode, defaultLanguage, timeRange]);

  const handleReconnect = () => {
    refetch();
  };

  const isHealthy = health?.status === 'ok';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Settings className="w-8 h-8 mr-3 text-gray-600" />
            Settings
          </h1>
          <p className="text-gray-600 mt-1">Configure dashboard preferences and monitor system health</p>
        </div>
      </div>

      {/* Backend Health Status */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Backend Health Status
          </h3>
          <button
            onClick={handleReconnect}
            disabled={loading}
            className="flex items-center space-x-2 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Reconnect</span>
          </button>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {isHealthy ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
              <span className="font-medium text-gray-900">Backend Connection</span>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${isHealthy ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {isHealthy ? 'Connected' : error ? 'Disconnected' : 'Checking...'}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Activity className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-gray-900">RSS Feeds Active</span>
            </div>
            <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
              Active
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Clock className="w-5 h-5 text-purple-600" />
              <span className="font-medium text-gray-900">Last Sync Time</span>
            </div>
            <span className="text-sm text-gray-600">
              {formatLastUpdated(lastUpdated)}
            </span>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">
              Backend not responding. Retrying automatically...
            </p>
          </div>
        )}
      </div>

      {/* Dashboard Preferences */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Dashboard Preferences</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Auto-Refresh</p>
              <p className="text-sm text-gray-600">Automatically refresh data every 2 minutes</p>
            </div>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${autoRefresh ? 'bg-blue-600' : 'bg-gray-300'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${autoRefresh ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Dark Mode</p>
              <p className="text-sm text-gray-600">Switch to dark theme</p>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${darkMode ? 'bg-blue-600' : 'bg-gray-300'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>

          <div>
            <label className="block font-medium text-gray-900 mb-2">Default Language</label>
            <select
              value={defaultLanguage}
              onChange={(e) => setDefaultLanguage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="en">English</option>
              <option value="hi">Hindi (हिन्दी)</option>
              <option value="kn">Kannada (ಕನ್ನಡ)</option>
              <option value="ta">Tamil (தமிழ்)</option>
              <option value="te">Telugu (తెలుగు)</option>
              <option value="bn">Bengali (বাংলা)</option>
              <option value="mr">Marathi (मराठी)</option>
              <option value="gu">Gujarati (ગુજરાતી)</option>
              <option value="ml">Malayalam (മലയാളം)</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-900 mb-2">Default Time Range</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* User Preferences */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Preferred Filters
          </h3>
          <button
            onClick={() => saveSettings(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block font-medium text-gray-900 mb-2">Preferred Category</label>
            <select
              value={preferredCategory}
              onChange={(e) => setPreferredCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="health">Health</option>
              <option value="education">Education</option>
              <option value="agriculture">Agriculture</option>
              <option value="policy">Policy</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="economy">Economy</option>
              <option value="defense">Defense</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-900 mb-2">Preferred Region</label>
            <select
              value={preferredRegion}
              onChange={(e) => setPreferredRegion(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Regions</option>
              <option value="Karnataka">Karnataka</option>
              <option value="Tamil Nadu">Tamil Nadu</option>
              <option value="Maharashtra">Maharashtra</option>
              <option value="Delhi">Delhi</option>
              <option value="West Bengal">West Bengal</option>
              <option value="Gujarat">Gujarat</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-900 mb-2">Preferred Sentiment</label>
            <select
              value={preferredSentiment}
              onChange={(e) => setPreferredSentiment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Application Name</p>
            <p className="font-medium text-gray-900">{health?.name || 'NewsScope India'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Environment</p>
            <p className="font-medium text-gray-900">{health?.env || 'Production'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">API Base URL</p>
            <p className="font-medium text-gray-900">http://localhost:8000</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Backend Status</p>
            <p className={`font-medium ${isHealthy ? 'text-green-600' : 'text-red-600'}`}>
              {isHealthy ? 'Operational' : 'Unavailable'}
            </p>
          </div>
        </div>
      </div>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-fade-in">
          <CheckCircle className="w-5 h-5" />
          <span>Settings updated successfully!</span>
        </div>
      )}
    </div>
  );
}
