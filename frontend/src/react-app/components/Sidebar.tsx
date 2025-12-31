import { 
  BarChart3, 
  Globe, 
  TrendingUp, 
  Map, 
  Settings, 
  FileText,
  Languages,
  AlertTriangle,
  MessageSquare
} from 'lucide-react';
import clsx from 'clsx';
import { useApi } from '@/react-app/hooks/useApi';

interface SidebarProps {
  isOpen: boolean;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'news', label: 'News Feed', icon: FileText },
  { id: 'assistant', label: 'AI Assistant', icon: MessageSquare },
  { id: 'alerts', label: 'PIB Alerts', icon: AlertTriangle, showBadge: true },
  { id: 'sentiment', label: 'Sentiment Analysis', icon: TrendingUp },
  { id: 'geography', label: 'Geographic View', icon: Map },
  { id: 'languages', label: 'Language Insights', icon: Languages },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ isOpen, activeTab, onTabChange }: SidebarProps) {
  // Fetch unread alert count (requires authentication)
  const { data: alertCountData } = useApi<{ count: number }>('/pib/alerts/count/unread', [], undefined, true);
  const unreadAlertCount = alertCountData?.count || 0;

  return (
    <aside className={clsx(
      "glass-dark text-white transition-all duration-500 flex flex-col border-r border-white/10 shadow-2xl",
      isOpen ? "w-64" : "w-16"
    )}>
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center space-x-3 group">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-blue-500/50 transition-all duration-300 group-hover:scale-110">
            <Globe className="w-6 h-6 text-white" />
          </div>
          {isOpen && (
            <div className="animate-fade-in-up">
              <h2 className="font-bold text-lg bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">NewsScope</h2>
              <p className="text-gray-400 text-xs">PIB Dashboard</p>
            </div>
          )}
        </div>
      </div>

      <nav className="flex-1 pt-6">
        <ul className="space-y-2 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const showBadge = item.showBadge && unreadAlertCount > 0;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onTabChange(item.id)}
                  className={clsx(
                    "w-full flex items-center px-3 py-3 rounded-xl transition-all duration-300 relative group overflow-hidden",
                    activeTab === item.id
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-105"
                      : "text-gray-300 hover:bg-white/5 hover:text-white hover:scale-105"
                  )}
                >
                  {activeTab === item.id && (
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 animate-pulse" />
                  )}
                  <Icon className="w-5 h-5 flex-shrink-0 group-hover:scale-110 transition-transform duration-300 relative z-10" />
                  {isOpen && (
                    <span className="ml-3 truncate font-medium relative z-10">{item.label}</span>
                  )}
                  {showBadge && (
                    <span className={clsx(
                      "absolute flex items-center justify-center rounded-full bg-gradient-to-br from-red-500 to-pink-600 text-white text-xs font-bold shadow-lg animate-pulse",
                      isOpen ? "right-2 top-2 min-w-[20px] h-5 px-1.5" : "right-0 top-0 w-3 h-3"
                    )}>
                      {isOpen && unreadAlertCount}
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className={clsx("flex items-center", isOpen ? "justify-between" : "justify-center")}>
          <div className="relative">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <div className="absolute inset-0 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
          </div>
          {isOpen && (
            <span className="text-sm text-gray-400 font-medium">Live Monitoring</span>
          )}
        </div>
      </div>
    </aside>
  );
}
