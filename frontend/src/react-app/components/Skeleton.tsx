interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  variant?: 'text' | 'circular' | 'rectangular';
}

export default function Skeleton({ className = '', width, height, variant = 'text' }: SkeletonProps) {
  const baseClasses = 'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:1000px_100%]';
  
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  const style = {
    width: width || undefined,
    height: height || undefined,
  };

  return (
    <div 
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
    />
  );
}

export function NewsCardSkeleton() {
  return (
    <div className="glass p-6 rounded-2xl border border-white/20">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 space-y-3">
          <Skeleton width="80%" height="24px" />
          <Skeleton width="60%" height="20px" />
          <div className="flex items-center space-x-2">
            <Skeleton variant="circular" width="40px" height="40px" />
            <div className="flex-1 space-y-2">
              <Skeleton width="120px" height="14px" />
              <Skeleton width="100px" height="14px" />
            </div>
          </div>
        </div>
        <Skeleton variant="circular" width="40px" height="40px" />
      </div>
      <div className="space-y-2 mb-4">
        <Skeleton width="100%" height="16px" />
        <Skeleton width="90%" height="16px" />
        <Skeleton width="75%" height="16px" />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          <Skeleton width="80px" height="24px" className="rounded-full" />
          <Skeleton width="60px" height="24px" className="rounded-full" />
        </div>
        <Skeleton width="70px" height="24px" className="rounded-full" />
      </div>
    </div>
  );
}

export function DashboardStatsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="glass p-6 rounded-2xl border border-white/20">
          <div className="flex items-center justify-between mb-4">
            <Skeleton width="100px" height="16px" />
            <Skeleton variant="circular" width="48px" height="48px" />
          </div>
          <Skeleton width="80px" height="32px" className="mb-2" />
          <Skeleton width="120px" height="14px" />
        </div>
      ))}
    </div>
  );
}
