import { TrendingUp, FileText, Globe, BarChart, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import AnimatedCounter from './AnimatedCounter';
import GlassCard from './GlassCard';

interface StatsCardProps {
  title: string;
  value: number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ComponentType<{ className?: string }>;
  gradient: string;
}

function StatsCard({ title, value, change, trend, icon: Icon, gradient }: StatsCardProps) {
  const TrendIcon = trend === 'up' ? ArrowUp : trend === 'down' ? ArrowDown : Minus;
  
  return (
    <GlassCard className="group p-6 relative overflow-hidden bg-gradient-to-br from-gray-800 to-gray-900">
      {/* Animated gradient background */}
      <div className={`absolute inset-0 opacity-5 group-hover:opacity-15 transition-opacity duration-500 ${gradient}`} />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-semibold text-gray-300 uppercase tracking-wider">{title}</p>
          <div className={`p-3 rounded-xl ${gradient} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
        </div>
        
        <div className="text-4xl font-bold text-white mb-2 drop-shadow-lg">
          <AnimatedCounter value={value} />
        </div>
        
        {change && (
          <div className={`flex items-center space-x-1 text-sm font-semibold ${
            trend === 'up' ? 'text-green-400' : 
            trend === 'down' ? 'text-red-400' : 'text-gray-300'
          }`}>
            <TrendIcon className="w-4 h-4" />
            <span>{change}</span>
          </div>
        )}
      </div>
      
      {/* Decorative corner element */}
      <div className="absolute -right-8 -bottom-8 w-24 h-24 rounded-full bg-gradient-to-br from-white/10 to-transparent group-hover:scale-150 transition-transform duration-500" />
    </GlassCard>
  );
}

interface DashboardStatsProps {
  stats: {
    totalArticles: number;
    todayArticles: number;
    averageSentiment: number;
    topCategories: Array<{ category: string; count: number }>;
    totalChangePercent?: number | null;
    todayChangePercent?: number | null;
  };
}

export default function DashboardStats({ stats }: DashboardStatsProps) {
  // Handle null/undefined stats
  if (!stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="text-gray-500">Loading statistics...</div>
      </div>
    );
  }

  const sentimentLabel = stats.averageSentiment > 0.1 ? 'Positive' : 
                        stats.averageSentiment < -0.1 ? 'Negative' : 'Neutral';
  
  const topCategory = stats.topCategories && stats.topCategories.length > 0 
    ? stats.topCategories[0].category 
    : 'General';
  
  // Format percentage change text
  const formatChangeText = (percent: number | null | undefined, period: string) => {
    if (percent === null || percent === undefined) {
      return null;
    }
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent}% from ${period}`;
  };
  
  const totalChange = formatChangeText(stats.totalChangePercent, 'last month');
  const todayChange = formatChangeText(stats.todayChangePercent, 'yesterday');
  
  // Determine trend direction
  const getTrend = (percent: number | null | undefined): 'up' | 'down' | 'neutral' => {
    if (percent === null || percent === undefined) return 'neutral';
    if (percent > 0) return 'up';
    if (percent < 0) return 'down';
    return 'neutral';
  };
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCard
        title="Total Articles"
        value={stats.totalArticles}
        change={totalChange || undefined}
        trend={getTrend(stats.totalChangePercent)}
        icon={FileText}
        gradient="bg-gradient-to-br from-blue-500 to-blue-700"
      />
      
      <StatsCard
        title="Today's Articles"
        value={stats.todayArticles}
        change={todayChange || undefined}
        trend={getTrend(stats.todayChangePercent)}
        icon={Globe}
        gradient="bg-gradient-to-br from-green-500 to-emerald-700"
      />
      
      <StatsCard
        title="Sentiment Score"
        value={Math.round(stats.averageSentiment * 100)}
        change={sentimentLabel}
        trend={stats.averageSentiment > 0 ? 'up' : stats.averageSentiment < 0 ? 'down' : 'neutral'}
        icon={TrendingUp}
        gradient="bg-gradient-to-br from-purple-500 to-pink-700"
      />
      
      <StatsCard
        title="Top Category"
        value={stats.topCategories && stats.topCategories.length > 0 ? stats.topCategories[0].count : 0}
        change={topCategory}
        trend="neutral"
        icon={BarChart}
        gradient="bg-gradient-to-br from-orange-500 to-red-700"
      />
    </div>
  );
}
