import { useState } from 'react';
import { useApi } from '@/react-app/hooks/useApi';
import NewsCard from '@/react-app/components/NewsCard';
import { NewsArticle } from '@/shared/types';
import { Search, Filter, Calendar, TrendingUp, Globe, MapPin, Tag, Loader2, Download } from 'lucide-react';

export default function AdvancedFiltersPage() {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    sentiment: '',
    language: '',
    region: '',
    startDate: '',
    endDate: '',
    minSentimentScore: '',
    maxSentimentScore: '',
    source: '',
    tags: '',
  });

  const [appliedFilters, setAppliedFilters] = useState(filters);
  const [sortBy, setSortBy] = useState('published_at');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const queryParams = new URLSearchParams();
  Object.entries(appliedFilters).forEach(([key, value]) => {
    if (value) queryParams.set(key, value);
  });
  queryParams.set('sort', sortBy);
  queryParams.set('order', sortOrder);
  
  const { data: newsResp, loading, error } = useApi<{ items: NewsArticle[]; total: number }>(
    `/news?${queryParams.toString()}`,
    [appliedFilters, sortBy, sortOrder]
  );

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    setAppliedFilters(filters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      search: '',
      category: '',
      sentiment: '',
      language: '',
      region: '',
      startDate: '',
      endDate: '',
      minSentimentScore: '',
      maxSentimentScore: '',
      source: '',
      tags: '',
    };
    setFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
  };

  const exportResults = () => {
    const articles = newsResp?.items || [];
    if (!articles || articles.length === 0) return;
    
    const csvContent = [
      ['Title', 'Content', 'Source', 'Category', 'Sentiment', 'Language', 'Region', 'Published Date'].join(','),
      ...articles.map(article => [
        `"${(article.translated_title || article.title).replace(/"/g, '""')}"`,
        `"${(article.content ? article.content.substring(0, 100) : '').replace(/"/g, '""')}..."`,
        `"${article.source || ''}"`,
        (article.topic_labels && article.topic_labels[0]) || '',
        article.sentiment_label || '',
        (article.detected_language || article.language || ''),
        article.region || '',
        article.published_at || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `news_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Filters</h1>
          <p className="text-gray-600 mt-1">
            Powerful search and filtering tools for comprehensive news analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {newsResp && newsResp.items && newsResp.items.length > 0 && (
            <button
              onClick={exportResults}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export Results</span>
            </button>
          )}
        </div>
      </div>

      {/* Advanced Filters Panel */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Advanced Search & Filters
          </h3>
          <span className="text-sm text-gray-500">
            {newsResp ? `${newsResp.total} articles found` : 'Loading...'}
          </span>
        </div>
        
        {/* Search and Text Filters */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <Search className="w-4 h-4 mr-1" />
              Full Text Search
            </label>
            <input
              type="text"
              placeholder="Search in titles, content, and summaries..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <Tag className="w-4 h-4 mr-1" />
              Tags & Keywords
            </label>
            <input
              type="text"
              placeholder="Enter tags separated by commas..."
              value={filters.tags}
              onChange={(e) => handleFilterChange('tags', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Category and Classification Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              Sentiment
            </label>
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
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
              <Globe className="w-4 h-4 mr-1" />
              Language
            </label>
            <select
              value={filters.language}
              onChange={(e) => handleFilterChange('language', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Languages</option>
              <option value="hindi">Hindi</option>
              <option value="bengali">Bengali</option>
              <option value="tamil">Tamil</option>
              <option value="telugu">Telugu</option>
              <option value="marathi">Marathi</option>
              <option value="gujarati">Gujarati</option>
              <option value="kannada">Kannada</option>
              <option value="malayalam">Malayalam</option>
              <option value="punjabi">Punjabi</option>
              <option value="english">English</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
              <MapPin className="w-4 h-4 mr-1" />
              Region
            </label>
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

        {/* Date and Sentiment Score Ranges */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              Start Date
            </label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleFilterChange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleFilterChange('endDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min Sentiment Score</label>
            <input
              type="number"
              min="-1"
              max="1"
              step="0.1"
              placeholder="-1.0 to 1.0"
              value={filters.minSentimentScore}
              onChange={(e) => handleFilterChange('minSentimentScore', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Sentiment Score</label>
            <input
              type="number"
              min="-1"
              max="1"
              step="0.1"
              placeholder="-1.0 to 1.0"
              value={filters.maxSentimentScore}
              onChange={(e) => handleFilterChange('maxSentimentScore', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Source Filter and Sorting */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">News Source</label>
            <input
              type="text"
              placeholder="Enter source name..."
              value={filters.source}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="published_at">Published Date</option>
              <option value="sentiment_score">Sentiment Score</option>
              <option value="title">Title</option>
              <option value="category">Category</option>
              <option value="created_at">Added Date</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="desc">Newest First</option>
              <option value="asc">Oldest First</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4">
          <button
            onClick={applyFilters}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Apply Advanced Filters
          </button>
          <button
            onClick={clearFilters}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Clear All Filters
          </button>
        </div>
      </div>

      {/* Results Section */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2 text-gray-600">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Searching news articles...</span>
          </div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-medium">Error loading news articles</h3>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
  ) : !newsResp || !newsResp.items || newsResp.items.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg">No news articles found</p>
          <p className="text-gray-500 text-sm mt-2">Try adjusting your filters or search terms</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg">
            <span className="text-sm text-gray-600">
              Found {newsResp.total} articles matching your criteria
            </span>
            <span className="text-xs text-gray-500">
              Click any article to read the full story on the original news website
            </span>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {newsResp.items.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
