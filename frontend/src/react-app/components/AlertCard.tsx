import { AlertTriangle, CheckCircle, Clock, Mail } from 'lucide-react';
import { Alert } from '@/shared/types';

interface AlertCardProps {
  alert: Alert;
  onMarkAsRead: (alertId: number) => void;
}

export default function AlertCard({ alert, onMarkAsRead }: AlertCardProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />;
      case 'low':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-orange-200 bg-orange-50';
      case 'low':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`rounded-lg border p-4 ${getSeverityColor(alert.severity)} ${!alert.is_read ? 'ring-2 ring-blue-200' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getSeverityIcon(alert.severity)}
          <span className={`text-sm font-medium uppercase px-2 py-1 rounded ${
            alert.severity === 'high' ? 'bg-red-100 text-red-800' :
            alert.severity === 'medium' ? 'bg-orange-100 text-orange-800' :
            alert.severity === 'low' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {alert.severity} Priority
          </span>
          {!alert.is_read && (
            <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
          )}
        </div>
        
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          <span>{formatDate(alert.created_at)}</span>
        </div>
      </div>

      <h3 className="font-semibold text-gray-900 mb-2">{alert.title}</h3>
      <p className="text-gray-700 text-sm mb-3">{alert.description}</p>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm">
          <span className="text-gray-600">
            Sentiment Score: <span className="font-medium text-red-600">{alert.sentiment_score.toFixed(2)}</span>
          </span>
          
          <div className="flex items-center space-x-1">
            {alert.is_sent ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-green-600">Notifications Sent</span>
              </>
            ) : (
              <>
                <Mail className="w-4 h-4 text-orange-600" />
                <span className="text-orange-600">Sending Notifications...</span>
              </>
            )}
          </div>
        </div>

        {!alert.is_read && (
          <button
            onClick={() => onMarkAsRead(alert.id)}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
          >
            Mark as Read
          </button>
        )}
      </div>
    </div>
  );
}
