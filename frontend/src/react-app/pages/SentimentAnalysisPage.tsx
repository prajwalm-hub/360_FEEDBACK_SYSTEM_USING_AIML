import { useApi } from '@/react-app/hooks/useApi';
import { TrendingUp, TrendingDown, Minus, Loader2, RefreshCw, Clock, Download, BarChart3, Sparkles, Target, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { DashboardStats } from '@/shared/types';
import { useState } from 'react';
import PageTransition from '@/react-app/components/PageTransition';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import ScrollReveal from '@/react-app/components/ScrollReveal';
import AnimatedBackground from '@/react-app/components/AnimatedBackground';
import { motion } from 'framer-motion';

const COLORS = {
  positive: '#10B981',
  neutral: '#6B7280',
  negative: '#EF4444'
};

export default function SentimentAnalysisPage() {
  const [lastUpdated] = useState(new Date());
  const { data: stats, loading, error, refetch } = useApi<DashboardStats>('/metrics', [], 120000);

  // Transform data from metrics endpoint
  const data = stats ? {
    total_articles: stats.totalArticles || 0,
    positive_count: stats.sentimentTrends.reduce((sum, day) => sum + day.positive, 0),
    negative_count: stats.sentimentTrends.reduce((sum, day) => sum + day.negative, 0),
    neutral_count: stats.sentimentTrends.reduce((sum, day) => sum + day.neutral, 0),
    average_sentiment: stats.averageSentiment || 0,
    daily_trends: stats.sentimentTrends.slice(-7)
  } : null;

  const handleExport = () => {
    if (!data) return;
    
    const csvData = [
      ['Metric', 'Value'],
      ['Total Articles', data.total_articles.toString()],
      ['Positive Count', data.positive_count.toString()],
      ['Negative Count', data.negative_count.toString()],
      ['Neutral Count', data.neutral_count.toString()],
      ['Average Sentiment', data.average_sentiment.toFixed(3)],
      [''],
      ['Date', 'Positive', 'Negative', 'Neutral'],
      ...data.daily_trends.map(day => [day.date, day.positive.toString(), day.negative.toString(), day.neutral.toString()])
    ];
    
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sentiment-analysis-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2 text-gray-600">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading sentiment analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-medium">Error loading sentiment data</h3>
        <p className="text-red-600 text-sm mt-1">{error}</p>
      </div>
    );
  }

  const pieData = [
    { name: 'Positive', value: data?.positive_count || 0, color: COLORS.positive },
    { name: 'Neutral', value: data?.neutral_count || 0, color: COLORS.neutral },
    { name: 'Negative', value: data?.negative_count || 0, color: COLORS.negative }
  ];

  const total = (data?.positive_count || 0) + (data?.neutral_count || 0) + (data?.negative_count || 0);

  return (
    <PageTransition>
      <AnimatedBackground />
      <div className="space-y-6 relative z-10">
        {/* Header */}
        <ScrollReveal>
          <motion.div 
            className="flex items-center justify-between"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-600 via-pink-600 to-red-600 rounded-xl flex items-center justify-center animate-glow shadow-lg shadow-purple-300">
                  <Activity className="w-7 h-7 text-white" />
                </div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 bg-clip-text text-transparent">
                  Sentiment Analytics Dashboard
                </h1>
              </div>
              <p className="text-gray-600 mt-1 flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-yellow-500 animate-pulse" />
                <span>Real-time AI-powered sentiment analysis across Indian government news coverage</span>
              </p>
              <div className="flex items-center space-x-2 mt-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>Auto-updating • Last refreshed: Just now</span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <motion.button
                onClick={handleExport}
                disabled={!data}
                className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-md shadow-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Download className="w-4 h-4" />
                <span className="font-medium">Export CSV</span>
              </motion.button>
              <motion.button
                onClick={refetch}
                disabled={loading}
                className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all shadow-md shadow-blue-200 disabled:opacity-50"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="font-medium">Refresh</span>
              </motion.button>
            </div>
          </motion.div>
        </ScrollReveal>

        {/* Summary Cards */}
        <StaggerContainer className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <motion.div 
          variants={staggerItemVariants}
          className="bg-gradient-to-br from-white via-blue-50 to-blue-100 rounded-2xl p-6 border-2 border-blue-200 shadow-lg hover:shadow-xl transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-blue-700 mb-1">Total Articles</p>
              <p className="text-4xl font-bold bg-gradient-to-r from-blue-700 to-blue-900 bg-clip-text text-transparent">{data?.total_articles || 0}</p>
              <p className="text-xs text-blue-600 mt-1">Analyzed stories</p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
              <BarChart3 className="w-7 h-7 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={staggerItemVariants}
          className="bg-gradient-to-br from-green-50 via-green-100 to-emerald-100 rounded-2xl p-6 border-2 border-green-300 shadow-lg hover:shadow-xl transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-green-800 mb-1">Positive News</p>
              <p className="text-4xl font-bold bg-gradient-to-r from-green-700 to-green-900 bg-clip-text text-transparent">{data?.positive_count || 0}</p>
              <p className="text-xs text-green-700 mt-1 font-semibold">
                {total > 0 ? Math.round(((data?.positive_count || 0) / total) * 100) : 0}% of total
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-green-600 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
              <TrendingUp className="w-7 h-7 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={staggerItemVariants}
          className="bg-gradient-to-br from-gray-50 via-gray-100 to-slate-100 rounded-2xl p-6 border-2 border-gray-300 shadow-lg hover:shadow-xl transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-800 mb-1">Neutral News</p>
              <p className="text-4xl font-bold bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">{data?.neutral_count || 0}</p>
              <p className="text-xs text-gray-700 mt-1 font-semibold">
                {total > 0 ? Math.round(((data?.neutral_count || 0) / total) * 100) : 0}% of total
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-gray-600 to-slate-600 rounded-xl flex items-center justify-center shadow-lg">
              <Minus className="w-7 h-7 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={staggerItemVariants}
          className="bg-gradient-to-br from-red-50 via-red-100 to-pink-100 rounded-2xl p-6 border-2 border-red-300 shadow-lg hover:shadow-xl transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-red-800 mb-1">Negative News</p>
              <p className="text-4xl font-bold bg-gradient-to-r from-red-700 to-red-900 bg-clip-text text-transparent">{data?.negative_count || 0}</p>
              <p className="text-xs text-red-700 mt-1 font-semibold">
                {total > 0 ? Math.round(((data?.negative_count || 0) / total) * 100) : 0}% of total
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-red-600 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
              <TrendingDown className="w-7 h-7 text-white" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={staggerItemVariants}
          className="bg-gradient-to-br from-purple-50 via-purple-100 to-indigo-100 rounded-2xl p-6 border-2 border-purple-300 shadow-lg hover:shadow-xl transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-purple-800 mb-1">Avg Sentiment</p>
              <p className="text-4xl font-bold bg-gradient-to-r from-purple-700 to-purple-900 bg-clip-text text-transparent">{data?.average_sentiment?.toFixed(3) || '0.000'}</p>
              <p className="text-xs text-purple-700 mt-1 font-semibold">
                {(data?.average_sentiment || 0) > 0 ? '↑ Positive Trend' : (data?.average_sentiment || 0) < 0 ? '↓ Negative Trend' : '− Neutral'}
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <Target className="w-7 h-7 text-white" />
            </div>
          </div>
        </motion.div>
        </StaggerContainer>

        {/* Charts Row 1: Pie Chart and Bar Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <ScrollReveal>
          <motion.div 
            className="bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 shadow-lg hover:shadow-xl transition-all"
            whileHover={{ scale: 1.01 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Sentiment Distribution</h3>
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  animationDuration={800}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </ScrollReveal>

        {/* Bar Chart */}
        <ScrollReveal>
          <motion.div 
            className="bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 shadow-lg hover:shadow-xl transition-all"
            whileHover={{ scale: 1.01 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Sentiment Comparison</h3>
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pieData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar dataKey="value" fill="#3B82F6" animationDuration={800} radius={[8, 8, 0, 0]}>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </ScrollReveal>
        </div>

        {/* Line Chart - Daily Trends */}
        <ScrollReveal>
          <motion.div 
            className="bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 shadow-lg hover:shadow-xl transition-all"
            whileHover={{ scale: 1.005 }}
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">7-Day Sentiment Trends</h3>
                <p className="text-sm text-gray-600 mt-1">Track sentiment changes over the past week</p>
              </div>
              <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={data?.daily_trends || []}>
                <defs>
                  <linearGradient id="colorPositive" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.positive} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={COLORS.positive} stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorNeutral" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.neutral} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={COLORS.neutral} stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorNegative" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.negative} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={COLORS.negative} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="positive" 
                  stroke={COLORS.positive} 
                  fillOpacity={1}
                  fill="url(#colorPositive)"
                  strokeWidth={3}
                  dot={{ r: 5, fill: COLORS.positive, strokeWidth: 2, stroke: '#fff' }}
                  animationDuration={1000}
                />
                <Area 
                  type="monotone" 
                  dataKey="neutral" 
                  stroke={COLORS.neutral} 
                  fillOpacity={1}
                  fill="url(#colorNeutral)"
                  strokeWidth={3}
                  dot={{ r: 5, fill: COLORS.neutral, strokeWidth: 2, stroke: '#fff' }}
                  animationDuration={1000}
                />
                <Area 
                  type="monotone" 
                  dataKey="negative" 
                  stroke={COLORS.negative} 
                  fillOpacity={1}
                  fill="url(#colorNegative)"
                  strokeWidth={3}
                  dot={{ r: 5, fill: COLORS.negative, strokeWidth: 2, stroke: '#fff' }}
                  animationDuration={1000}
                />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>
        </ScrollReveal>

        {/* Key Insights */}
        <ScrollReveal>
          <motion.div 
            className="bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Key Insights</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2 bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-xl border border-blue-200">
                <h4 className="font-semibold text-blue-900 flex items-center space-x-2">
                  <Target className="w-5 h-5" />
                  <span>Dominant Sentiment</span>
                </h4>
                <p className="text-3xl font-bold" style={{ color: 
                  (data?.positive_count || 0) > (data?.negative_count || 0) && (data?.positive_count || 0) > (data?.neutral_count || 0) ? COLORS.positive :
                  (data?.negative_count || 0) > (data?.positive_count || 0) && (data?.negative_count || 0) > (data?.neutral_count || 0) ? COLORS.negative :
                  COLORS.neutral
                }}>
                  {(data?.positive_count || 0) > (data?.negative_count || 0) && (data?.positive_count || 0) > (data?.neutral_count || 0) ? '✓ Positive' :
                   (data?.negative_count || 0) > (data?.positive_count || 0) && (data?.negative_count || 0) > (data?.neutral_count || 0) ? '✗ Negative' :
                   '− Neutral'}
                </p>
                <p className="text-sm text-blue-700">Most common sentiment across articles</p>
              </div>

              <div className="space-y-2 bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-xl border border-purple-200">
                <h4 className="font-semibold text-purple-900 flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <span>Sentiment Ratio</span>
                </h4>
                <p className="text-sm text-purple-800 mt-2">
                  <span className="font-semibold text-lg">Positive to Negative:</span>
                  <span className="block text-3xl font-bold text-purple-900 mt-1">
                    {(data?.negative_count || 0) > 0 ? ((data?.positive_count || 0) / (data?.negative_count || 0)).toFixed(2) : 'N/A'}:1
                  </span>
                </p>
                <p className="text-sm text-purple-700">Balance indicator</p>
              </div>

              <div className="space-y-2 bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-xl border border-orange-200">
                <h4 className="font-semibold text-orange-900 flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Coverage Period</span>
                </h4>
                <p className="text-3xl font-bold text-orange-900 mt-2">7 Days</p>
                <p className="text-sm text-orange-700">Comprehensive news analysis window</p>
              </div>
            </div>
          </motion.div>
        </ScrollReveal>
      </div>
    </PageTransition>
  );
}
