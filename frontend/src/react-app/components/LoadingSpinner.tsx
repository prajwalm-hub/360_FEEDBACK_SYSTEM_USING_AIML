import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  fullScreen?: boolean;
}

export default function LoadingSpinner({ 
  size = 'md', 
  message = 'Loading...', 
  fullScreen = false 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-10 h-10',
  };

  const containerClass = fullScreen
    ? 'fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50'
    : 'flex items-center justify-center h-64';

  return (
    <div className={containerClass}>
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-md opacity-75 animate-pulse"></div>
          <div className="relative bg-white rounded-full p-3">
            <Loader2 className={`${sizeClasses[size]} text-blue-600 animate-spin`} />
          </div>
        </div>
        {message && (
          <p className="text-gray-600 font-medium animate-pulse">{message}</p>
        )}
      </div>
    </div>
  );
}
