import { useState, useEffect } from 'react';
import { useApi } from './useApi';
import { NewsArticle, DashboardStats } from '@/shared/types';

export function useMetrics(refreshInterval?: number) {
  const [metrics, setMetrics] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  
  const { data: newsData } = useApi<{items: NewsArticle[], total: number}>('/news?limit=100', [], refreshInterval);
  
  useEffect(() => {
    if (!newsData?.items) {
      setLoading(true);
      return;
    }
    
    const articles = newsData.items;
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    const todayArticles = articles.filter(a => new Date(a.collected_at) >= yesterday).length;
    
    const languageMap = new Map<string, number>();
    articles.forEach(a => {
      if (a.language) {
        languageMap.set(a.language, (languageMap.get(a.language) || 0) + 1);
      }
    });
    
    const categoryMap = new Map<string, number>();
    articles.forEach(a => {
      if (a.topic_labels) {
        a.topic_labels.forEach(topic => {
          categoryMap.set(topic, (categoryMap.get(topic) || 0) + 1);
        });
      }
    });
    
    const dayMap = new Map<string, {positive: number, neutral: number, negative: number}>();
    for (let i = 0; i < 7; i++) {
      const day = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      const dateStr = day.toISOString().split('T')[0];
      dayMap.set(dateStr, {positive: 0, neutral: 0, negative: 0});
    }
    
    articles.forEach(a => {
      const date = new Date(a.collected_at);
      if (date >= sevenDaysAgo) {
        const dateStr = date.toISOString().split('T')[0];
        const sentiment = dayMap.get(dateStr);
        if (sentiment && a.sentiment_label) {
          const label = a.sentiment_label.toLowerCase();
          if (label === 'positive') sentiment.positive++;
          else if (label === 'negative') sentiment.negative++;
          else sentiment.neutral++;
        }
      }
    });
    
    const sentimentTrends = Array.from(dayMap.entries())
      .map(([date, counts]) => ({date, ...counts}))
      .reverse();
    
    const avgSentiment = articles.reduce((sum, a) => sum + (a.sentiment_score || 0), 0) / (articles.length || 1);
    
    setMetrics({
      totalArticles: newsData.total,
      todayArticles,
      averageSentiment: avgSentiment,
      languageDistribution: Array.from(languageMap.entries()).map(([language, count]) => ({language, count})),
      topCategories: Array.from(categoryMap.entries()).map(([category, count]) => ({category, count})).slice(0, 10),
      sentimentTrends,
      totalChangePercent: null,
      todayChangePercent: null
    });
    setLoading(false);
  }, [newsData]);
  
  return { data: metrics, loading, refetch: () => {} };
}
