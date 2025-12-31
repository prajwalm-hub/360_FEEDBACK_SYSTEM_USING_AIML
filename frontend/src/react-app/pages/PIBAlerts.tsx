import { useState } from 'react';
import { useAutoRefresh } from '@/react-app/hooks/useAutoRefresh';
import { AlertTriangle, TrendingUp, TrendingDown, Minus, RefreshCw, Download, ExternalLink, Check, X, Clock, Filter } from 'lucide-react';
import { formatLastUpdated, cleanHtmlText } from '@/react-app/utils/textCleanup';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import PageTransition from '@/react-app/components/PageTransition';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import ScrollReveal from '@/react-app/components/ScrollReveal';
import { motion } from 'framer-motion';

interface PIBAlert {
  id: string;
  article_id: string;
  title: string;
  summary: string | null;
  link: string | null;
  language: string | null;
  sentiment_score: number | null;
  is_reviewed: boolean;
  reviewed_at: string | null;
  reviewed_by: string | null;
  email_sent: boolean;
  email_sent_at: string | null;
  created_at: string;
  updated_at: string;
}

interface AlertsResponse {
  items: PIBAlert[];
  total: number;
  unread_count: number;
}

const SENTIMENT_COLORS = {
  positive: '#10B981',
  neutral: '#6B7280',
  negative: '#EF4444'
};

export default function PIBAlerts() {
  const [statusFilter, setStatusFilter] = useState('all');
  const [languageFilter, setLanguageFilter] = useState('all');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data: alertsData, loading, error, refetch, lastUpdated } = useAutoRefresh<AlertsResponse>(
    `/pib/alerts?skip=${(page - 1) * limit}&limit=${limit}`,
    120000,
    true
  );

  const { data: countData } = useAutoRefresh<{ count: number }>('/pib/alerts/count/unread', 120000, true);

  const handleExport = () => {
    if (!alertsData?.items) return;
    
    const csvData = [
      ['Title', 'Summary', 'Sentiment Score', 'Language', 'Date', 'Status'],
      ...alertsData.items.map(alert => [
        alert.title,
        alert.summary || '',
        alert.sentiment_score?.toString() || '',
        alert.language || '',
        new Date(alert.created_at).toLocaleString(),
        alert.is_reviewed ? 'Read' : 'Unread'
      ])
    ];
    
    const csvContent = csvData.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pib-alerts-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleMarkAsRead = async (alertId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please login to perform this action');
        window.location.href = '/login';
        return;
      }
      const response = await fetch(`/api/pib/alerts/${alertId}/review`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_reviewed: true })
      });
      if (response.status === 401) {
        alert('Session expired. Please login again.');
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      refetch();
    } catch (err) {
      console.error('Failed to mark as read:', err);
      alert('Failed to update alert');
    }
  };

  const handleDelete = async (alertId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Please login to perform this action');
        window.location.href = '/login';
        return;
      }
      const response = await fetch(`/api/pib/alerts/${alertId}`, { 
        method: 'DELETE',
        headers: { 
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.status === 401) {
        alert('Session expired. Please login again.');
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
      }
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      refetch();
    } catch (err) {
      console.error('Failed to delete alert:', err);
      alert('Failed to delete alert');
    }
  };

  const alerts = alertsData?.items || [];
  const filteredAlerts = alerts.filter(alert => {
    if (statusFilter !== 'all' && (statusFilter === 'unread' ? alert.is_reviewed : !alert.is_reviewed)) return false;
    if (languageFilter !== 'all' && alert.language !== languageFilter) return false;
    return true;
  });

  const stats = {
    total: alertsData?.total || 0,
    unread: alertsData?.unread_count || 0,
    negative: alerts.length, // All alerts are negative sentiment
    positive: 0,
    neutral: 0
  };

  const pieData = [
    { name: 'Negative', value: stats.negative, color: SENTIMENT_COLORS.negative },
    { name: 'Reviewed', value: stats.total - stats.unread, color: '#6B7280' },
    { name: 'Unread', value: stats.unread, color: '#F59E0B' }
  ];

  const getSentimentBadge = (score: number | null) => {
    if (!score) return <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">Unknown</span>;
    const percentage = Math.round(score * 100);
    return (
      <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
        Negative ({percentage}%)
      </span>
    );
  };

  if (loading && !alertsData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2 text-gray-600">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Loading alerts...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <AlertTriangle className="w-8 h-8 mr-3 text-orange-600" />
            PIB Alert Dashboard
          </h1>
          <p className="text-gray-600 mt-1">Real-time government news alerts and monitoring</p>
          <div className="flex items-center space-x-2 mt-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>Last updated: {formatLastUpdated(lastUpdated)}</span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleExport}
            disabled={!alertsData?.items.length}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>Export Alerts</span>
          </button>
          <button
            onClick={refetch}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <p className="text-sm font-medium text-gray-600">Total Alerts</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
        </div>
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
          <p className="text-sm font-medium text-orange-700">Unread</p>
          <p className="text-3xl font-bold text-orange-900 mt-2">{stats.unread}</p>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 border border-red-200">
          <p className="text-sm font-medium text-red-700">Negative Alerts</p>
          <p className="text-3xl font-bold text-red-900 mt-2">{stats.negative}</p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
          <p className="text-sm font-medium text-green-700">Reviewed</p>
          <p className="text-3xl font-bold text-green-900 mt-2">{stats.total - stats.unread}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <p className="text-xs font-medium text-gray-600 mb-2">Distribution</p>
          <ResponsiveContainer width="100%" height={80}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={30} dataKey="value">
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 border border-gray-200">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="unread">Unread</option>
            <option value="read">Read</option>
          </select>

          <select
            value={languageFilter}
            onChange={(e) => setLanguageFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Languages</option>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="kn">Kannada</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {error ? (
          <div className="p-6 text-center text-red-600">Error loading alerts: {error}</div>
        ) : filteredAlerts.length === 0 ? (
          <div className="p-12 text-center">
            <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No active alerts right now</h3>
            <p className="text-gray-600">Check back later for new government news alerts</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Alert</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sentiment Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Language</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email Sent</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredAlerts.map((alert) => (
                  <tr key={alert.id} className={`hover:bg-gray-50 transition-colors ${!alert.is_reviewed ? 'bg-orange-50' : ''}`}>
                    <td className="px-6 py-4">
                      <div className="flex items-start space-x-3">
                        <TrendingDown className="w-4 h-4 text-red-600 mt-1" />
                        <div className="flex-1">
                          <p className={`text-sm ${!alert.is_reviewed ? 'font-bold' : 'font-medium'} text-gray-900`}>
                            {cleanHtmlText(alert.title)}
                          </p>
                          {alert.summary && (
                            <p className="text-xs text-gray-600 mt-1 line-clamp-2">{cleanHtmlText(alert.summary)}</p>
                          )}
                          {!alert.is_reviewed && (
                            <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-orange-100 text-orange-800 rounded-full">
                              New
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">{getSentimentBadge(alert.sentiment_score)}</td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-900">{alert.language?.toUpperCase() || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4">
                      {alert.email_sent ? (
                        <span className="flex items-center text-xs text-green-600">
                          <Check className="w-3 h-3 mr-1" />
                          Sent
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">Pending</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-600">
                        {new Date(alert.created_at).toLocaleDateString()}
                      </span>
                      <br />
                      <span className="text-xs text-gray-400">
                        {new Date(alert.created_at).toLocaleTimeString()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {!alert.is_reviewed && (
                          <button
                            onClick={() => handleMarkAsRead(alert.id)}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="Mark as Read"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        )}
                        {alert.link && (
                          <a
                            href={alert.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                            title="View Article"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                        <button
                          onClick={() => handleDelete(alert.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                          title="Delete"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {filteredAlerts.length > 0 && (
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-gray-200">
          <p className="text-sm text-gray-600">
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, stats.total)} of {stats.total} alerts
          </p>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-3 py-1 text-sm text-gray-600">Page {page}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page * limit >= stats.total}
              className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
