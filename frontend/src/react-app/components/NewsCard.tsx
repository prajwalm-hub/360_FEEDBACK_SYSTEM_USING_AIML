import { Calendar, Globe, TrendingUp, TrendingDown, Minus, ExternalLink, Sparkles } from 'lucide-react';
import { NewsArticle } from '@/shared/types';
import ClassificationBadge from './ClassificationBadge';
import GlassCard from './GlassCard';

interface NewsCardProps {
  article: NewsArticle;
}

const LANGUAGE_NAMES: { [key: string]: string } = {
  en: 'English',
  hi: 'Hindi',
  kn: 'Kannada',
  ta: 'Tamil',
  te: 'Telugu',
  bn: 'Bengali',
  gu: 'Gujarati',
  mr: 'Marathi',
  pa: 'Punjabi',
  ml: 'Malayalam',
  or: 'Odia',
  ur: 'Urdu',
};

const SCRIPT_FONTS: { [key: string]: string } = {
  'Devanagari': 'font-devanagari',
  'Tamil': 'font-tamil',
  'Telugu': 'font-telugu',
  'Kannada': 'font-kannada',
  'Bengali': 'font-bengali',
  'Gujarati': 'font-gujarati',
  'Malayalam': 'font-malayalam',
  'Odia': 'font-odia',
  'Gurmukhi': 'font-gurmukhi',
  'Arabic': 'font-urdu', // Urdu uses Arabic script
};

export default function NewsCard({ article }: NewsCardProps) {
  const hasTranslation = !!(article.translated_title || article.translated_summary);
  const isNonEnglish = article.detected_language && article.detected_language !== 'en';
  
  // Get script-specific font class for regional languages
  const getScriptFont = () => {
    if (article.detected_script && article.detected_script !== 'Latin') {
      return SCRIPT_FONTS[article.detected_script] || '';
    }
    return '';
  };
  
  const scriptFontClass = getScriptFont();
  const getSentimentIcon = (sentiment: string | null) => {
    switch (sentiment) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-green-700" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-700" />;
      default:
        return <Minus className="w-4 h-4 text-blue-700" />;
    }
  };

  const getSentimentColor = (sentiment: string | null) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-700 bg-green-100 border-2 border-green-300';
      case 'negative':
        return 'text-red-700 bg-red-100 border-2 border-red-300';
      default:
        return 'text-blue-700 bg-blue-100 border-2 border-blue-300';
    }
  };

  const getCategoryColor = (category: string | null) => {
    const colors: { [key: string]: string } = {
      'Health': 'bg-blue-100 text-blue-800',
      'Education': 'bg-green-100 text-green-800',
      'Policy': 'bg-purple-100 text-purple-800',
      'Governance': 'bg-orange-100 text-orange-800',
      'Economy': 'bg-yellow-100 text-yellow-800',
      'Technology': 'bg-indigo-100 text-indigo-800',
      'Environment': 'bg-teal-100 text-teal-800',
    };
    return colors[category || ''] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'Unknown date';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleCardClick = () => {
    if (article.url && (article.url.startsWith('http://') || article.url.startsWith('https://'))) {
      window.open(article.url, '_blank,', 'noopener,noreferrer');
    }
  };

  return (
    <GlassCard 
      className="group p-5 relative overflow-hidden border border-white/20 hover:shadow-xl hover:border-blue-300 transition-all duration-300"
    >
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div className="relative z-10 space-y-4">
        {/* Header Section: Title + Date/Language/Region */}
        <div className="space-y-2">
          {/* Title Section */}
          <div>
            {isNonEnglish && hasTranslation ? (
              <>
                <h3 className={`text-xl font-bold text-gray-900 dark:text-white mb-2 line-clamp-2 ${scriptFontClass}`}>
                  {article.title}
                </h3>
                <h4 className="text-base font-semibold text-blue-700 dark:text-blue-400 line-clamp-2 flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-blue-500 flex-shrink-0" />
                  <span>{article.translated_title || 'Translation not available'}</span>
                </h4>
              </>
            ) : (
              <h3 className={`text-xl font-bold text-gray-900 dark:text-white line-clamp-2 ${scriptFontClass}`}>
                {article.title}
              </h3>
            )}
          </div>
          
          {/* Meta Information: Date, Language, Region */}
          <div className="flex items-center flex-wrap gap-3 text-sm">
            <div className="flex items-center space-x-1.5 text-gray-600 dark:text-gray-400">
              <Calendar className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium">{formatDate(article.published_at)}</span>
            </div>
            
            {article.detected_language && (
              <div className="flex items-center space-x-1.5 px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
                <Globe className="w-4 h-4 flex-shrink-0" />
                <span className="font-medium">
                  {LANGUAGE_NAMES[article.detected_language] || article.detected_language}
                </span>
                {article.detected_script && article.detected_script !== 'Latin' && (
                  <span className="text-xs opacity-75">({article.detected_script})</span>
                )}
              </div>
            )}
            
            {article.region && (
              <span className="px-2.5 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-xs font-medium">
                {article.region}
              </span>
            )}
            
            {hasTranslation && isNonEnglish && (
              <div className="flex items-center space-x-1 px-2.5 py-1 bg-green-50 border border-green-200 text-green-700 rounded-full text-xs font-medium">
                <Globe className="w-3 h-3 flex-shrink-0" />
                <span>AI Translated</span>
              </div>
            )}
          </div>
        </div>

        {/* Article Summary/Content */}
        <div className="space-y-2">
          {isNonEnglish && hasTranslation ? (
            <>
              <p className={`text-gray-700 dark:text-gray-300 line-clamp-3 leading-relaxed ${scriptFontClass}`}>
                {article.summary || (article.content ? article.content.substring(0, 200) + '...' : '')}
              </p>
              <p className="text-gray-600 dark:text-gray-400 line-clamp-3 text-sm leading-relaxed border-l-2 border-blue-300 pl-3">
                {article.translated_summary || 'Translation not available'}
              </p>
            </>
          ) : (
            <p className={`text-gray-700 dark:text-gray-300 line-clamp-3 leading-relaxed ${scriptFontClass}`}>
              {article.summary || (article.content ? article.content.substring(0, 200) + '...' : '')}
            </p>
          )}
        </div>

        {/* Footer: Categories, Source, and Sentiment */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center flex-wrap gap-2">
            {/* Content Classification Badge */}
            {article.content_category && (
              <ClassificationBadge
                category={article.content_category}
                subCategory={article.content_sub_category || undefined}
                confidence={article.classification_confidence || undefined}
                size="sm"
              />
            )}
            
            {article.topic_labels && article.topic_labels.length > 0 && (
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${getCategoryColor(article.topic_labels[0])}`}>
                {article.topic_labels[0]}
              </span>
            )}
            
            {article.source && (
              <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 rounded-full text-xs font-medium">
                {article.source}
              </span>
            )}
          </div>

          {(() => {
            const sentiment = (article.sentiment_label || 'neutral').toLowerCase();
            return (
              <div className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${getSentimentColor(sentiment)}`}>
                {getSentimentIcon(sentiment)}
                <span className="capitalize">{sentiment}</span>
                {typeof article.sentiment_score === 'number' && (
                  <span className="ml-0.5">({article.sentiment_score.toFixed(2)})</span>
                )}
              </div>
            );
          })()}
        </div>

        {/* Read Full Article Button */}
        {article.url && (
          <button
            onClick={() => {
              if (article.url && (article.url.startsWith('http://') || article.url.startsWith('https://'))) {
                window.open(article.url, '_blank', 'noopener,noreferrer');
              }
            }}
            className="w-full mt-3 flex items-center justify-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-medium transition-all shadow-md hover:shadow-lg group"
          >
            <span>Read Full Article</span>
            <ExternalLink className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
        )}
      </div>
    </GlassCard>
  );
}
