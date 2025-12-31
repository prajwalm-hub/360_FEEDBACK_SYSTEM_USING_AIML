import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface EnhancedCardProps {
  children: ReactNode;
  className?: string;
  gradient?: string;
  hover?: boolean;
}

export default function EnhancedCard({ 
  children, 
  className = '', 
  gradient = 'from-blue-500/10 to-purple-500/10',
  hover = true 
}: EnhancedCardProps) {
  return (
    <motion.div
      className={`relative group ${className}`}
      whileHover={hover ? { scale: 1.02, y: -5 } : {}}
      transition={{ duration: 0.3 }}
    >
      {/* Gradient border effect */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-2xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
      
      {/* Card content */}
      <div className="relative bg-white/90 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-lg group-hover:shadow-2xl transition-all duration-300">
        {/* Shine effect */}
        <div className="absolute inset-0 rounded-2xl overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000" />
        </div>
        
        {children}
      </div>
    </motion.div>
  );
}
