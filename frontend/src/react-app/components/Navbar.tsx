import { Search, Settings, Menu, Newspaper, Bell, User } from 'lucide-react';

interface NavbarProps {
  onToggleSidebar: () => void;
  onSettingsClick?: () => void;
}

export default function Navbar({ onToggleSidebar, onSettingsClick }: NavbarProps) {
  const userRaw = typeof window !== 'undefined' ? localStorage.getItem('newsscope_user') : null;
  const user = userRaw ? JSON.parse(userRaw) as { username?: string; userType?: string } : null;
  const initials = user?.username ? user.username.charAt(0).toUpperCase() : 'A';
  const displayName = user?.username ? user.username : 'Admin User';
  const email = user?.userType === 'pib_officer' ? 'pib@gov.in' : 'admin@gov.in';
  
  return (
    <nav className="glass sticky top-0 z-50 px-6 py-3 border-b border-white/20 shadow-lg">
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2.5 text-gray-700 hover:text-gray-900 hover:bg-white/50 rounded-xl transition-all duration-300 hover:scale-110"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 via-orange-600 to-green-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-orange-500/50 transition-all duration-300 group-hover:scale-110">
              <Newspaper className="text-white w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-orange-600 to-green-600 bg-clip-text text-transparent">
                NewsScope India
              </h1>
              <p className="text-xs text-gray-600 font-medium">360° Regional News Monitoring</p>
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-3">
          {/* Search Bar */}
          <div className="relative group hidden md:block">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 group-focus-within:text-blue-500 transition-colors" />
            <input
              type="text"
              placeholder="Search news articles..."
              className="pl-10 pr-4 py-2.5 glass border border-white/30 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 w-80 transition-all duration-300 focus:w-96 text-sm"
            />
          </div>
          
          {/* Notifications */}
          <button className="relative p-2.5 text-gray-700 hover:text-gray-900 hover:bg-white/50 rounded-xl transition-all duration-300 hover:scale-110 group">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="absolute -bottom-10 right-0 px-2 py-1 text-xs text-white bg-gray-900 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Notifications
            </span>
          </button>
          
          {/* Settings */}
          <button 
            onClick={onSettingsClick}
            className="p-2.5 text-gray-700 hover:text-gray-900 hover:bg-white/50 rounded-xl transition-all duration-300 hover:scale-110 hover:rotate-90 group"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
            <span className="absolute -bottom-10 right-0 px-2 py-1 text-xs text-white bg-gray-900 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Settings
            </span>
          </button>
          
          {/* User Profile */}
          <div className="relative group">
            <button className="flex items-center space-x-2 pl-2 pr-3 py-2 glass border border-white/30 rounded-xl hover:shadow-lg transition-all duration-300 hover:scale-105">
              <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-green-600 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-lg">
                {initials}
              </div>
              <span className="text-sm font-medium text-gray-700 hidden lg:block">{displayName}</span>
            </button>
            
            {/* Dropdown */}
            <div className="absolute right-0 top-full mt-2 w-56 glass border border-white/30 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform origin-top-right scale-95 group-hover:scale-100">
              <div className="p-4 border-b border-white/20">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-green-600 rounded-lg flex items-center justify-center text-white font-bold">
                    {initials}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{displayName}</p>
                    <p className="text-xs text-gray-600">{email}</p>
                  </div>
                </div>
              </div>
              <div className="p-2">
                <button className="w-full flex items-center space-x-2 px-3 py-2.5 text-sm text-gray-700 hover:bg-white/50 rounded-lg transition-all duration-300 group/item">
                  <User className="w-4 h-4 group-hover/item:scale-110 transition-transform" />
                  <span>Profile</span>
                </button>
                <button
                  onClick={() => {
                    localStorage.removeItem('newsscope_user');
                    window.location.href = '/login';
                  }}
                  className="w-full flex items-center space-x-2 px-3 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-all duration-300 mt-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
