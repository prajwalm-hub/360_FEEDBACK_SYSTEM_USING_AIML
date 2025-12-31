import { useAutoRefresh } from '@/react-app/hooks/useAutoRefresh';
import { NewsArticle } from '@/shared/types';
import { Map, MapPin, Loader2, RefreshCw, Globe, Clock, Sparkles } from 'lucide-react';
import { cleanHtmlText, formatLastUpdated } from '@/react-app/utils/textCleanup';
import PageTransition from '@/react-app/components/PageTransition';
import AnimatedBackground from '@/react-app/components/AnimatedBackground';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import ScrollReveal from '@/react-app/components/ScrollReveal';
import { motion } from 'framer-motion';

interface RegionData {
  region: string;
  count: number;
  articles: NewsArticle[];
}

export default function GeographicViewPage() {
  const { data: newsResp, loading, error, refetch, lastUpdated } = useAutoRefresh<{ items: NewsArticle[]; total: number }>('/news', 120000);

  const handleRefresh = () => {
    refetch();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2 text-gray-600">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading geographic data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-medium">Error loading geographic data</h3>
        <p className="text-red-600 text-sm mt-1">{error}</p>
      </div>
    );
  }

  const regionData: { [key: string]: RegionData } = {};
  const articles = newsResp?.items || [];
  if (articles) {
    articles.forEach(article => {
      const region = article.region || 'Unknown Region';
      if (!regionData[region]) {
        regionData[region] = {
          region,
          count: 0,
          articles: []
        };
      }
      regionData[region].count++;
      regionData[region].articles.push(article);
    });
  }

  const sortedRegions = Object.values(regionData).sort((a, b) => b.count - a.count);

  const getRegionColor = (count: number, maxCount: number) => {
    const intensity = count / maxCount;
    if (intensity > 0.8) return 'bg-red-600';
    if (intensity > 0.6) return 'bg-orange-500';
    if (intensity > 0.4) return 'bg-yellow-500';
    if (intensity > 0.2) return 'bg-green-500';
    return 'bg-blue-500';
  };

  const maxCount = Math.max(...sortedRegions.map(r => r.count), 1);

  return (
    <PageTransition>
      <AnimatedBackground />
      <div className="space-y-6 relative z-10">
        <ScrollReveal>
          <motion.div 
            className="flex items-center justify-between"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-300 animate-glow">
                  <Map className="w-7 h-7 text-white" />
                </div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-pink-600 bg-clip-text text-transparent">
                  Geographic Distribution
                </h1>
              </div>
              <p className="text-gray-600 mt-2 flex items-center space-x-2 font-medium">
                <Globe className="w-4 h-4 text-blue-500 animate-pulse" />
                <span>News coverage distribution across Indian regions</span>
                <Sparkles className="w-4 h-4 text-yellow-500 animate-pulse" />
              </p>
              <div className="flex items-center space-x-2 mt-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>Last updated: {formatLastUpdated(lastUpdated)}</span>
              </div>
            </div>
            <motion.button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl hover:from-orange-700 hover:to-red-700 transition-all shadow-lg shadow-orange-300 disabled:opacity-50 font-semibold"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </motion.button>
          </motion.div>
        </ScrollReveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedRegions.map((regionInfo, index) => (
          <div key={regionInfo.region} className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${getRegionColor(regionInfo.count, maxCount)}`}>
                  <MapPin className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{regionInfo.region}</h3>
                  <p className="text-sm text-gray-600">#{index + 1} in coverage</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">{regionInfo.count}</p>
                <p className="text-sm text-gray-600">articles</p>
              </div>
            </div>

            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Coverage Share</span>
                <span>{((regionInfo.count / (articles?.length || 1)) * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${getRegionColor(regionInfo.count, maxCount)}`}
                  style={{ width: `${(regionInfo.count / maxCount) * 100}%` }}
                ></div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Articles</h4>
              <div className="space-y-2">
                {regionInfo.articles.slice(0, 3).map((article) => (
                  <div key={article.id} className="text-xs text-gray-600 p-2 bg-gray-50 rounded">
                    <p className="font-medium line-clamp-1">{cleanHtmlText(article.translated_title || article.title)}</p>
                    <p className="text-gray-500 mt-1">
                      {(article.topic_labels && article.topic_labels[0]) || 'General'} • {article.detected_language || article.language}
                    </p>
                  </div>
                ))}
                {regionInfo.articles.length > 3 && (
                  <p className="text-xs text-gray-500 text-center">
                    +{regionInfo.articles.length - 3} more articles
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
        </div>

        <div className="bg-white rounded-xl p-8 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <Globe className="w-5 h-5 mr-2" />
          Interactive Map View
        </h3>
        
        <div className="relative bg-gradient-to-br from-blue-50 to-green-50 rounded-lg p-8 min-h-96 flex items-center justify-center">
          <div className="text-center">
            <div className="w-32 h-32 mx-auto mb-4 bg-gradient-to-br from-saffron-500 to-green-600 rounded-full flex items-center justify-center">
              <Map className="w-16 h-16 text-white" />
            </div>
            <h4 className="text-xl font-bold text-gray-900 mb-2">India News Coverage Map</h4>
            <p className="text-gray-600 mb-4">Interactive regional visualization</p>
            
            <div className="inline-flex items-center space-x-4 bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-600 rounded"></div>
                <span className="text-sm text-gray-600">High Coverage</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                <span className="text-sm text-gray-600">Medium Coverage</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span className="text-sm text-gray-600">Low Coverage</span>
              </div>
            </div>
          </div>
        </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Coverage Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{sortedRegions.length}</p>
            <p className="text-sm text-gray-600">Active Regions</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{articles?.length || 0}</p>
            <p className="text-sm text-gray-600">Total Articles</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-orange-600">
              {sortedRegions.length > 0 ? Math.round((articles?.length || 0) / sortedRegions.length) : 0}
            </p>
            <p className="text-sm text-gray-600">Avg. per Region</p>
          </div>
        </div>
        </div>
      </div>
    </PageTransition>
  );
}
