import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  gradient: string;
  iconColor?: string;
}

export default function StatCard({ 
  icon: Icon, 
  label, 
  value, 
  trend, 
  trendValue,
  gradient,
  iconColor = 'text-white'
}: StatCardProps) {
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  };

  const trendIcons = {
    up: '↗',
    down: '↘',
    neutral: '→'
  };

  return (
    <motion.div
      className="relative group"
      whileHover={{ y: -5, scale: 1.02 }}
      transition={{ duration: 0.3 }}
    >
      {/* Glow effect */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-60 transition-opacity duration-300`} />
      
      {/* Card */}
      <div className="relative bg-white/95 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 shadow-lg group-hover:shadow-2xl transition-all duration-300">
        <div className="flex items-start justify-between mb-4">
          {/* Icon */}
          <motion.div
            className={`p-3 rounded-xl bg-gradient-to-br ${gradient} shadow-lg`}
            whileHover={{ rotate: [0, -10, 10, 0], scale: 1.1 }}
            transition={{ duration: 0.5 }}
          >
            <Icon className={`w-6 h-6 ${iconColor}`} />
          </motion.div>
          
          {/* Trend */}
          {trend && trendValue && (
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-lg bg-gray-50 ${trendColors[trend]}`}>
              <span className="text-lg">{trendIcons[trend]}</span>
              <span className="text-sm font-semibold">{trendValue}</span>
            </div>
          )}
        </div>
        
        {/* Label */}
        <p className="text-sm font-medium text-gray-600 uppercase tracking-wider mb-2">
          {label}
        </p>
        
        {/* Value */}
        <p className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
          {value}
        </p>
        
        {/* Animated underline */}
        <div className="mt-4 h-1 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            className={`h-full bg-gradient-to-r ${gradient}`}
            initial={{ width: '0%' }}
            whileInView={{ width: '100%' }}
            transition={{ duration: 1, ease: 'easeOut' }}
            viewport={{ once: true }}
          />
        </div>
      </div>
    </motion.div>
  );
}
