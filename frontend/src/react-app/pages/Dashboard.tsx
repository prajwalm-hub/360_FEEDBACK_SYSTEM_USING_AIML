import { useApi } from '@/react-app/hooks/useApi';
import DashboardStats from '@/react-app/components/DashboardStats';
import SentimentChart from '@/react-app/components/SentimentChart';
import LanguageDistribution from '@/react-app/components/LanguageDistribution';
import CategoryChart from '@/react-app/components/CategoryChart';
import { DashboardStatsSkeleton } from '@/react-app/components/Skeleton';
import MeshGradient from '@/react-app/components/MeshGradient';
import FloatingParticles from '@/react-app/components/FloatingParticles';
import AnimatedBackground from '@/react-app/components/AnimatedBackground';
import PageTransition from '@/react-app/components/PageTransition';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import ScrollReveal from '@/react-app/components/ScrollReveal';
import { motion } from 'framer-motion';
import { DashboardStats as DashboardStatsType } from '@/shared/types';
import { RefreshCw, AlertCircle, TrendingUp, Activity, Sparkles } from 'lucide-react';

export default function Dashboard() {
  const { data: stats, loading, error, refetch } = useApi<DashboardStatsType>('/metrics', [], 180000);

  const handleRefresh = () => {
    refetch();
  };

  if (loading && !stats) {
    return (
      <div className="space-y-6 relative">
        <MeshGradient />
        <FloatingParticles />
        <div className="relative z-10 animate-fade-in-up">
          <DashboardStatsSkeleton />
        </div>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="min-h-[400px] flex items-center justify-center relative">
        <MeshGradient />
        <div className="max-w-md w-full glass rounded-2xl p-8 text-center relative z-10 shadow-2xl animate-scale-in">
          <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-float">
            <AlertCircle className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-2xl font-bold bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Dashboard Unavailable
          </h3>
          <p className="text-red-600 text-sm mb-4">{error}</p>
          <p className="text-gray-600 text-sm mb-6">
            The backend API might be down or the database is not connected. 
            Click retry or check that the backend is running on port 8000.
          </p>
          <button
            onClick={handleRefresh}
            className="group relative flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 transition-all duration-300 mx-auto shadow-lg hover:shadow-xl hover:scale-105"
          >
            <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="space-y-6 relative">
        <MeshGradient />
        <FloatingParticles />
        <div className="relative z-10 animate-fade-in-up">
          <DashboardStatsSkeleton />
        </div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="space-y-6 relative">
        <AnimatedBackground />
        <MeshGradient />
        <FloatingParticles />
        
        {/* Header with gradient */}
        <ScrollReveal>
          <div className="flex items-center justify-between relative z-10">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-300 animate-glow">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Dashboard Overview
                </h1>
              </div>
              <p className="text-gray-600 flex items-center space-x-2 mt-2">
                <Activity className="w-4 h-4 text-green-500 animate-pulse" />
                <span className="font-medium">Real-time monitoring of regional news across India</span>
                <Sparkles className="w-4 h-4 text-yellow-500 animate-pulse" />
              </p>
            </div>
            <motion.button
              onClick={handleRefresh}
              className="group relative flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-lg shadow-blue-300 hover:shadow-xl hover:shadow-purple-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw className="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
              <span className="font-semibold">Refresh Data</span>
            </motion.button>
          </div>
        </ScrollReveal>

        {/* Stats with animation */}
        <ScrollReveal delay={0.1}>
          <DashboardStats stats={stats} />
        </ScrollReveal>

        {/* Charts Grid */}
        <StaggerContainer className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div variants={staggerItemVariants}>
            <SentimentChart data={stats.sentimentTrends} />
          </motion.div>
          <motion.div variants={staggerItemVariants}>
            <LanguageDistribution data={stats.languageDistribution} />
          </motion.div>
        </StaggerContainer>

        <ScrollReveal delay={0.4}>
          <CategoryChart data={stats.topCategories} />
        </ScrollReveal>
      </div>
    </PageTransition>
  );
}
