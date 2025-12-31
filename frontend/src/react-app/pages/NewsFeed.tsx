import { useState } from 'react';
import { useApi } from '@/react-app/hooks/useApi';
import NewsCard from '@/react-app/components/NewsCard';
import LanguageSelector from '@/react-app/components/LanguageSelector';
import LoadingSpinner from '@/react-app/components/LoadingSpinner';
import EmptyState from '@/react-app/components/EmptyState';
import BackToTop from '@/react-app/components/BackToTop';
import PageTransition from '@/react-app/components/PageTransition';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import AnimatedBackground from '@/react-app/components/AnimatedBackground';
import { motion } from 'framer-motion';

import { NewsArticle } from '@/shared/types';
import { Search, Filter, Wifi, WifiOff, TrendingUp, TrendingDown, Minus, Newspaper, Sparkles } from 'lucide-react';

export default function NewsFeed() {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    sentiment: '',
    language: 'all',
    region: '',
  });

  const [appliedFilters, setAppliedFilters] = useState(filters);
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  const queryParams = new URLSearchParams();
  queryParams.set('limit', '200');
  if (appliedFilters.search) queryParams.set('q', appliedFilters.search);
  if (appliedFilters.category) queryParams.set('category', appliedFilters.category);
  if (appliedFilters.sentiment) queryParams.set('sentiment', appliedFilters.sentiment);
  if (appliedFilters.language && appliedFilters.language !== 'all') queryParams.set('language', appliedFilters.language);
  if (appliedFilters.region) queryParams.set('region', appliedFilters.region);
  
  // Auto-refresh every 2 minutes (120000ms) if enabled
  const refreshInterval = autoRefresh ? 120000 : undefined;
  
  const { data, loading, error, refetch } = useApi<{items: NewsArticle[], total: number}>(
    `/news?${queryParams.toString()}`,
    [appliedFilters],
    refreshInterval
  );
  
  // Fetch language stats
  const { data: languageStats } = useApi<Array<{ language: string; language_name: string; count: number }>>(
    '/analytics/languages',
    []
  );
  

  
  const articles = data?.items || [];
  const totalArticles = data?.total || 0;

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };
  
  const handleLanguageChange = (language: string) => {
    setFilters(prev => ({ ...prev, language }));
    setAppliedFilters(prev => ({ ...prev, language }));
  };

  const applyFilters = () => {
    setAppliedFilters(filters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      search: '',
      category: '',
      sentiment: '',
      language: 'all',
      region: '',
    };
    setFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
  };

  return (
    <PageTransition>
      <AnimatedBackground />
      <div className="space-y-6 relative z-10">
        <motion.div 
          className="flex items-center justify-between"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center animate-glow">
                <Newspaper className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-pink-600 bg-clip-text text-transparent">
                Live News Feed
              </h1>
            </div>
            <p className="text-gray-600 mt-1 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-yellow-500 animate-pulse" />
              <span>
                Real-time news from Indian government sources and regional media
                {autoRefresh && " • Auto-refreshing every 2 minutes"}
              </span>
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <motion.button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl transition-all shadow-md ${
                autoRefresh
                  ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 shadow-green-200' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {autoRefresh ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span className="font-medium">{autoRefresh ? 'Live' : 'Paused'}</span>
            </motion.button>
            <motion.button
              onClick={refetch}
              className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl hover:from-orange-700 hover:to-red-700 transition-all shadow-md shadow-orange-200"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Search className="w-4 h-4" />
              <span className="font-medium">Refresh Now</span>
            </motion.button>
          </div>
        </motion.div>


      {/* Quick Sentiment Filter Pills */}
      <motion.div 
        className="bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl rounded-2xl border border-gray-200/50 p-6 shadow-lg"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 flex-wrap gap-2">
            <span className="text-sm font-semibold text-gray-700 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-purple-500" />
              <span>Quick Filter:</span>
            </span>
            <div className="flex items-center space-x-2 flex-wrap gap-2">
              <motion.button
                onClick={() => {
                  setFilters(prev => ({ ...prev, sentiment: '' }));
                  setAppliedFilters(prev => ({ ...prev, sentiment: '' }));
                }}
                className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${
                  appliedFilters.sentiment === ''
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-200'
                    : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-blue-400 hover:shadow-md'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                All News
              </motion.button>
              <motion.button
                onClick={() => {
                  setFilters(prev => ({ ...prev, sentiment: 'positive' }));
                  setAppliedFilters(prev => ({ ...prev, sentiment: 'positive' }));
                }}
                className={`px-5 py-2 rounded-full text-sm font-semibold transition-all flex items-center space-x-1.5 ${
                  appliedFilters.sentiment === 'positive'
                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg shadow-green-200'
                    : 'bg-white text-green-700 border-2 border-green-300 hover:border-green-500 hover:shadow-md'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <TrendingUp className="w-4 h-4" />
                <span>Positive</span>
              </motion.button>
              <motion.button
                onClick={() => {
                  setFilters(prev => ({ ...prev, sentiment: 'neutral' }));
                  setAppliedFilters(prev => ({ ...prev, sentiment: 'neutral' }));
                }}
                className={`px-5 py-2 rounded-full text-sm font-semibold transition-all flex items-center space-x-1.5 ${
                  appliedFilters.sentiment === 'neutral'
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-200'
                    : 'bg-white text-blue-700 border-2 border-blue-300 hover:border-blue-500 hover:shadow-md'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Minus className="w-4 h-4" />
                <span>Neutral</span>
              </motion.button>
              <motion.button
                onClick={() => {
                  setFilters(prev => ({ ...prev, sentiment: 'negative' }));
                  setAppliedFilters(prev => ({ ...prev, sentiment: 'negative' }));
                }}
                className={`px-5 py-2 rounded-full text-sm font-semibold transition-all flex items-center space-x-1.5 ${
                  appliedFilters.sentiment === 'negative'
                    ? 'bg-gradient-to-r from-red-600 to-pink-600 text-white shadow-lg shadow-red-200'
                    : 'bg-white text-red-700 border-2 border-red-300 hover:border-red-500 hover:shadow-md'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <TrendingDown className="w-4 h-4" />
                <span>Negative</span>
              </motion.button>
            </div>
          </div>
          {appliedFilters.sentiment && (
            <motion.span 
              className="text-xs text-gray-600 font-medium bg-gray-100 px-3 py-1 rounded-full"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              Showing {appliedFilters.sentiment} articles
            </motion.span>
          )}
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div 
        className="bg-gradient-to-br from-white/90 to-gray-50/90 backdrop-blur-xl rounded-2xl border border-gray-200/50 p-6 shadow-lg"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <Filter className="w-4 h-4 text-white" />
            </div>
            <span>Advanced Filters</span>
          </h3>
          <p className="text-sm text-gray-600">
            Refine your search across categories, sentiment, language, and region
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search articles..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Categories</option>
              <option value="Health">Health</option>
              <option value="Education">Education</option>
              <option value="Policy">Policy</option>
              <option value="Governance">Governance</option>
              <option value="Economy">Economy</option>
              <option value="Technology">Technology</option>
              <option value="Environment">Environment</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sentiment</label>
            <select
              value={filters.sentiment}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
            <LanguageSelector
              selectedLanguage={filters.language}
              onLanguageChange={handleLanguageChange}
              languageStats={languageStats || []}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
            <select
              value={filters.region}
              onChange={(e) => handleFilterChange('region', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Regions</option>
              <option value="North India">North India</option>
              <option value="South India">South India</option>
              <option value="East India">East India</option>
              <option value="West India">West India</option>
              <option value="Central India">Central India</option>
              <option value="Northeast India">Northeast India</option>
            </select>
          </div>
        </div>

        <div className="flex space-x-3">
          <motion.button
            onClick={applyFilters}
            className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md shadow-purple-200"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Apply Filters
          </motion.button>
          <motion.button
            onClick={clearFilters}
            className="px-6 py-2.5 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all font-medium"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Clear All
          </motion.button>
        </div>
      </motion.div>

      {/* News Articles */}
      {loading ? (
        <LoadingSpinner message="Loading news articles..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-medium">Error loading news articles</h3>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      ) : !articles || articles.length === 0 ? (
        <EmptyState
          icon={Newspaper}
          title="No news articles found"
          description="Try adjusting your filters or check back later for new government news updates."
          action={{
            label: "Clear Filters",
            onClick: clearFilters
          }}
        />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-3 rounded-lg border border-blue-200">
            <span className="text-sm font-medium text-blue-900">
              Found {totalArticles} article{totalArticles !== 1 ? 's' : ''} • Showing {articles.length}
            </span>
            <span className="text-xs text-blue-700">
              {appliedFilters.sentiment && `${appliedFilters.sentiment} sentiment • `}
              {appliedFilters.category && `${appliedFilters.category} • `}
              {appliedFilters.language !== 'all' && appliedFilters.language && `${appliedFilters.language} language`}
            </span>
          </div>
          
          <StaggerContainer className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {articles.map((article, index) => (
              <motion.div key={article.id} variants={staggerItemVariants}>
                <NewsCard article={article} />
              </motion.div>
            ))}
          </StaggerContainer>
          
          {/* Pagination Info */}
          <div className="flex items-center justify-center bg-white px-4 py-3 rounded-lg border border-gray-200 mt-6">
            <span className="text-sm text-gray-700">
              Showing 1 to {articles.length} of {totalArticles} articles
            </span>
          </div>
        </div>
      )}
      
      <BackToTop />
      </div>
    </PageTransition>
  );
}
