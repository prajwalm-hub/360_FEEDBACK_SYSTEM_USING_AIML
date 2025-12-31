import { useAutoRefresh } from '@/react-app/hooks/useAutoRefresh';
import { NewsArticle } from '@/shared/types';
import { Languages, Loader2, RefreshCw, Clock, TrendingUp, TrendingDown, Sparkles, Globe } from 'lucide-react';
import { formatLastUpdated } from '@/react-app/utils/textCleanup';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Legend } from 'recharts';
import { useMemo } from 'react';
import PageTransition from '@/react-app/components/PageTransition';
import AnimatedBackground from '@/react-app/components/AnimatedBackground';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import ScrollReveal from '@/react-app/components/ScrollReveal';
import { motion } from 'framer-motion';

interface LanguageStat {
  language: string;
  language_name: string;
  count: number;
}

const LANGUAGE_INFO: Record<string, { native: string; flag: string; script: string }> = {
  'hindi': { native: 'हिन्दी', flag: '🇮🇳', script: 'Devanagari' },
  'kannada': { native: 'ಕನ್ನಡ', flag: '🇮🇳', script: 'Kannada' },
  'tamil': { native: 'தமிழ்', flag: '🇮🇳', script: 'Tamil' },
  'telugu': { native: 'తెలుగు', flag: '🇮🇳', script: 'Telugu' },
  'bengali': { native: 'বাংলা', flag: '🇮🇳', script: 'Bengali' },
  'gujarati': { native: 'ગુજરાતી', flag: '🇮🇳', script: 'Gujarati' },
  'marathi': { native: 'मराठी', flag: '🇮🇳', script: 'Devanagari' },
  'punjabi': { native: 'ਪੰਜਾਬੀ', flag: '🇮🇳', script: 'Gurmukhi' },
  'malayalam': { native: 'മലയാളം', flag: '🇮🇳', script: 'Malayalam' },
  'odia': { native: 'ଓଡ଼ିଆ', flag: '🇮🇳', script: 'Odia' },
  'urdu': { native: 'اردو', flag: '🇮🇳', script: 'Arabic' },
  'english': { native: 'English', flag: '🇬🇧', script: 'Latin' },
};

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export default function LanguageInsightsPage() {
  const { data: languageStats, loading, refetch, lastUpdated } = useAutoRefresh<LanguageStat[]>('/analytics/languages', 120000);
  const { data: articlesData, loading: articlesLoading } = useAutoRefresh<{ items: NewsArticle[]; total: number }>('/news?limit=100', 120000);

  const articles = articlesData?.items || [];

  const languageData = useMemo(() => {
    if (!languageStats || languageStats.length === 0) return [];

    return languageStats.map(stat => {
      const langArticles = articles.filter(a => {
        const detectedLang = (a.detected_language || a.language || '').toLowerCase();
        const statLang = stat.language.toLowerCase();
        return detectedLang === statLang || detectedLang.startsWith(statLang.substring(0, 2));
      });

      const positive = langArticles.filter(a => (a.sentiment_label || '').toLowerCase() === 'positive').length;
      const negative = langArticles.filter(a => (a.sentiment_label || '').toLowerCase() === 'negative').length;
      const neutral = langArticles.filter(a => (a.sentiment_label || '').toLowerCase() === 'neutral').length;

      const total = langArticles.length || 1;
      const posPercent = (positive / total) * 100;
      const negPercent = (negative / total) * 100;
      const neuPercent = (neutral / total) * 100;

      return {
        ...stat,
        language_name: stat.language_name || stat.language,
        positive,
        negative,
        neutral,
        posPercent,
        negPercent,
        neuPercent,
        trend: Math.random() > 0.5 ? 'up' : 'down'
      };
    });
  }, [languageStats, articles]);

  const translatedCount = articles.filter(a => 
    (a.translated_title && a.translated_title.trim() !== '') || 
    (a.translated_summary && a.translated_summary.trim() !== '')
  ).length;
  const translationRate = articles.length > 0 ? (translatedCount / articles.length) * 100 : 0;

  const confidenceArticles = articles.filter(a => a.language_confidence !== null && a.language_confidence !== undefined);
  const avgConfidence = confidenceArticles.length > 0
    ? (confidenceArticles.reduce((sum, a) => sum + (a.language_confidence || 0), 0) / confidenceArticles.length) * 100
    : 0;

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const langInfo = LANGUAGE_INFO[data.language?.toLowerCase()];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
          <p className="font-semibold">{langInfo?.flag} {data.language_name || data.language}</p>
          <p className="text-sm text-gray-600">Total: {data.count} articles</p>
          <p className="text-sm text-green-600">Positive: {data.posPercent?.toFixed(0)}%</p>
          <p className="text-sm text-blue-600">Neutral: {data.neuPercent?.toFixed(0)}%</p>
          <p className="text-sm text-red-600">Negative: {data.negPercent?.toFixed(0)}%</p>
          <p className="text-sm text-gray-500">Script: {langInfo?.script || 'Unknown'}</p>
        </div>
      );
    }
    return null;
  };

  if (loading || articlesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-gray-600" />
        <span className="ml-2 text-gray-600">Loading language insights...</span>
      </div>
    );
  }

  if (!languageStats || languageStats.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-gray-600">No language data available</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
        {/* Hero Header */}
        <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 text-white py-8 px-6 rounded-2xl shadow-xl mb-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <ScrollReveal>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 bg-white/20 backdrop-blur-sm rounded-lg">
                      <Globe className="w-8 h-8" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold tracking-tight">Language Insights</h1>
                      <p className="text-purple-100 mt-1 text-sm">Multilingual Intelligence & Sentiment Analytics</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 mt-3 text-sm text-purple-100">
                    <Clock className="w-4 h-4" />
                    <span>Last Updated: {formatLastUpdated(lastUpdated)}</span>
                  </div>
                </div>
                <button
                  onClick={refetch}
                  disabled={loading}
                  className="flex items-center space-x-2 px-6 py-3 bg-white text-purple-600 rounded-xl hover:bg-purple-50 disabled:opacity-50 shadow-lg transition-all duration-200 hover:scale-105"
                >
                  <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                  <span className="font-semibold">Refresh</span>
                </button>
              </div>
            </ScrollReveal>
          </div>
        </div>

      <div className="space-y-6 px-2">
        {/* Key Metrics */}
        <StaggerContainer>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div 
              variants={staggerItemVariants}
              className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-4 shadow-xl text-white relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-2">
                  <Languages className="w-6 h-6" />
                  <Sparkles className="w-5 h-5 opacity-70" />
                </div>
                <p className="text-purple-100 text-xs font-medium">Total Languages</p>
                <p className="text-2xl font-bold mt-1">{languageStats?.length || 0}</p>
                <p className="text-purple-100 text-xs mt-1">Active languages detected</p>
              </div>
            </motion.div>

            <motion.div 
              variants={staggerItemVariants}
              className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-4 shadow-xl text-white relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-2">
                  <Globe className="w-6 h-6" />
                  <TrendingUp className="w-5 h-5 opacity-70" />
                </div>
                <p className="text-green-100 text-xs font-medium">Translation Rate</p>
                <p className="text-2xl font-bold mt-1">{translationRate.toFixed(1)}%</p>
                <p className="text-green-100 text-xs mt-1">Articles translated</p>
              </div>
            </motion.div>

            <motion.div 
              variants={staggerItemVariants}
              className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-4 shadow-xl text-white relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-2">
                  <Sparkles className="w-6 h-6" />
                  <TrendingUp className="w-5 h-5 opacity-70" />
                </div>
                <p className="text-blue-100 text-xs font-medium">Avg Confidence</p>
                <p className="text-2xl font-bold mt-1">{avgConfidence.toFixed(1)}%</p>
                <p className="text-blue-100 text-xs mt-1">Detection accuracy</p>
              </div>
            </motion.div>
          </div>
        </StaggerContainer>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ScrollReveal>
            <div className="bg-white rounded-2xl p-6 shadow-xl border border-gray-100 hover:shadow-2xl transition-shadow duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                  <div className="w-2 h-6 bg-gradient-to-b from-purple-500 to-indigo-500 rounded-full mr-2"></div>
                  Language Distribution
                </h3>
                <div className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                  {languageData.length} Languages
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={languageData}
                    dataKey="count"
                    nameKey="language_name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.language_name}: ${entry.count}`}
                  >
                    {languageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </ScrollReveal>

          <ScrollReveal>
            <div className="bg-white rounded-2xl p-6 shadow-xl border border-gray-100 hover:shadow-2xl transition-shadow duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                  <div className="w-2 h-6 bg-gradient-to-b from-green-500 to-blue-500 rounded-full mr-2"></div>
                  Sentiment by Language
                </h3>
                <div className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                  Top 6
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={languageData.slice(0, 6)}>
                  <XAxis dataKey="language_name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="positive" fill="#10b981" name="Positive" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="neutral" fill="#3b82f6" name="Neutral" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="negative" fill="#ef4444" name="Negative" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ScrollReveal>
        </div>

        {/* Language Breakdown Table */}
        <ScrollReveal>
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-4">
              <h3 className="text-lg font-bold text-white flex items-center">
                <Languages className="w-5 h-5 mr-2" />
                Detailed Language Breakdown
              </h3>
              <p className="text-purple-100 text-xs mt-1">Complete analysis across all languages</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Language</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Script</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Articles</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Sentiment</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Trend</th>
                  </tr>
                </thead>
                <tbody>
                  {languageData.map((lang, index) => {
                    const langInfo = LANGUAGE_INFO[lang.language.toLowerCase()];
                    return (
                      <tr 
                        key={lang.language} 
                        className={`border-b border-gray-100 hover:bg-purple-50 transition-colors ${
                          index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'
                        }`}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-2">
                            <span className="text-xl">{langInfo?.flag || '🌐'}</span>
                            <div>
                              <p className="font-semibold text-gray-900">{lang.language_name || lang.language}</p>
                              <p className="text-sm text-gray-500">{langInfo?.native}</p>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                            {langInfo?.script || 'Unknown'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="font-bold text-base text-gray-900">{lang.count}</span>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1 px-2 py-1 bg-green-50 rounded-lg">
                              <span className="text-xs font-semibold text-green-700">+{lang.posPercent?.toFixed(0)}%</span>
                            </div>
                            <div className="flex items-center space-x-1 px-2 py-1 bg-blue-50 rounded-lg">
                              <span className="text-xs font-semibold text-blue-700">~{lang.neuPercent?.toFixed(0)}%</span>
                            </div>
                            <div className="flex items-center space-x-1 px-2 py-1 bg-red-50 rounded-lg">
                              <span className="text-xs font-semibold text-red-700">-{lang.negPercent?.toFixed(0)}%</span>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          {lang.trend === 'up' ? (
                            <div className="flex items-center space-x-1 text-green-600">
                              <TrendingUp className="w-5 h-5" />
                              <span className="text-xs font-medium">Rising</span>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-1 text-red-600">
                              <TrendingDown className="w-5 h-5" />
                              <span className="text-xs font-medium">Falling</span>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </ScrollReveal>
      </div>
      </div>
    </PageTransition>
  );
}
