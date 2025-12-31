import { useState } from 'react';
import Navbar from '@/react-app/components/Navbar';
import Sidebar from '@/react-app/components/Sidebar';
import AlertNotification from '@/react-app/components/AlertNotification';
import ErrorBoundary from '@/react-app/components/ErrorBoundary';
import Dashboard from '@/react-app/pages/Dashboard';
import NewsFeed from '@/react-app/pages/NewsFeed';
import PIBAlerts from '@/react-app/pages/PIBAlerts';
import PIBOfficersPage from '@/react-app/pages/PIBOfficersPage';
import SentimentAnalysisPage from '@/react-app/pages/SentimentAnalysisPage';
import GeographicViewPage from '@/react-app/pages/GeographicViewPage';
import LanguageInsightsPage from '@/react-app/pages/LanguageInsightsPage';
import AdvancedAnalytics from '@/react-app/pages/AdvancedAnalytics';

import SettingsPage from '@/react-app/pages/SettingsPage';
import RAGAssistant from '@/react-app/components/RAGAssistant';
import { useApi } from '@/react-app/hooks/useApi';
import { Alert } from '@/shared/types';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('news');
  const { data: notifications } = useApi<Alert[]>('/alerts/notifications');

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleDismissAlert = async (alertId: number) => {
    try {
      await fetch(`/alerts/${alertId}/read`, { method: 'POST' });
      window.location.reload();
    } catch (error) {
      console.error('Failed to dismiss alert:', error);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <ErrorBoundary><Dashboard /></ErrorBoundary>;
      case 'news':
        return <ErrorBoundary><NewsFeed /></ErrorBoundary>;
      case 'assistant':
        return <ErrorBoundary><RAGAssistant apiBaseUrl="http://localhost:8000/api" language="en" /></ErrorBoundary>;
      case 'alerts':
        return <ErrorBoundary><PIBAlerts /></ErrorBoundary>;
      case 'pib-officers':
        return <ErrorBoundary><PIBOfficersPage /></ErrorBoundary>;
      case 'sentiment':
        return <ErrorBoundary><SentimentAnalysisPage /></ErrorBoundary>;
      case 'geography':
        return <ErrorBoundary><GeographicViewPage /></ErrorBoundary>;
      case 'languages':
        return <ErrorBoundary><LanguageInsightsPage /></ErrorBoundary>;
      case 'settings':
        return <ErrorBoundary><SettingsPage /></ErrorBoundary>;
      default:
        return <ErrorBoundary><Dashboard /></ErrorBoundary>;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        isOpen={sidebarOpen} 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar onToggleSidebar={toggleSidebar} onSettingsClick={() => setActiveTab('settings')} />
        
        <main className="flex-1 overflow-auto p-6">
          {renderContent()}
        </main>
      </div>

      {/* Alert Notifications */}
      {notifications && (
        <AlertNotification 
          alerts={notifications} 
          onDismiss={handleDismissAlert}
        />
      )}
    </div>
  );
}
