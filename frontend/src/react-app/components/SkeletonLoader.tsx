import { motion } from 'framer-motion';
import { cn } from '@/react-app/utils/cn';

interface SkeletonLoaderProps {
  className?: string;
  count?: number;
  height?: string;
}

export default function SkeletonLoader({ 
  className = '', 
  count = 1,
  height = 'h-4'
}: SkeletonLoaderProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={cn(
            'bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg',
            'dark:from-gray-700 dark:via-gray-600 dark:to-gray-700',
            'animate-shimmer bg-[length:200%_100%]',
            height,
            className
          )}
          style={{ marginBottom: index < count - 1 ? '0.75rem' : 0 }}
        />
      ))}
    </>
  );
}

export function NewsCardSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-lg"
    >
      <div className="flex items-start space-x-4">
        <SkeletonLoader className="w-24 h-24 rounded-xl flex-shrink-0" />
        <div className="flex-1 space-y-3">
          <SkeletonLoader className="w-3/4" height="h-6" />
          <SkeletonLoader count={2} height="h-4" />
          <div className="flex space-x-2">
            <SkeletonLoader className="w-20" height="h-6" />
            <SkeletonLoader className="w-24" height="h-6" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
