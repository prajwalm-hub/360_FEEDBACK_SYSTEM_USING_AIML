import { useState, useEffect } from 'react';
import { X, AlertTriangle, Bell } from 'lucide-react';
import { Alert } from '@/shared/types';

interface AlertNotificationProps {
  alerts: Alert[];
  onDismiss: (alertId: number) => void;
}

export default function AlertNotification({ alerts, onDismiss }: AlertNotificationProps) {
  const [visibleAlerts, setVisibleAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    // Show only unread alerts from the last hour
    const recentAlerts = alerts
      .filter(alert => !alert.is_read)
      .filter(alert => {
        const alertTime = new Date(alert.created_at);
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        return alertTime > oneHourAgo;
      })
      .slice(0, 3); // Show max 3 notifications

    setVisibleAlerts(recentAlerts);
  }, [alerts]);

  if (visibleAlerts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm">
      {visibleAlerts.map((alert) => (
        <div
          key={alert.id}
          className={`bg-white rounded-lg shadow-lg border-l-4 p-4 ${
            alert.severity === 'high' ? 'border-red-500' :
            alert.severity === 'medium' ? 'border-orange-500' :
            'border-yellow-500'
          } animate-slide-in`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div className={`p-1 rounded ${
                alert.severity === 'high' ? 'bg-red-100' :
                alert.severity === 'medium' ? 'bg-orange-100' :
                'bg-yellow-100'
              }`}>
                <AlertTriangle className={`w-4 h-4 ${
                  alert.severity === 'high' ? 'text-red-600' :
                  alert.severity === 'medium' ? 'text-orange-600' :
                  'text-yellow-600'
                }`} />
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <Bell className="w-4 h-4 text-gray-600" />
                  <span className="text-xs font-medium text-gray-600 uppercase">
                    {alert.severity} Priority Alert
                  </span>
                </div>
                <h4 className="font-medium text-gray-900 text-sm mb-1">
                  {alert.title}
                </h4>
                <p className="text-gray-700 text-xs leading-relaxed">
                  {alert.description.length > 100 
                    ? alert.description.substring(0, 100) + '...'
                    : alert.description
                  }
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Sentiment: {alert.sentiment_score.toFixed(2)}
                </p>
              </div>
            </div>
            <button
              onClick={() => onDismiss(alert.id)}
              className="ml-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
