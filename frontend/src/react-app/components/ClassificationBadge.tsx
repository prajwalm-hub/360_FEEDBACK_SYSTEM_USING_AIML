import { Shield, Users, Film, Trophy, AlertTriangle, Briefcase, HelpCircle } from 'lucide-react';

interface ClassificationBadgeProps {
  category: string;
  subCategory?: string;
  confidence?: number;
  size?: 'sm' | 'md' | 'lg';
}

const CATEGORY_CONFIG = {
  Government: {
    icon: Shield,
    color: 'bg-green-100 text-green-800 border-green-300',
    darkColor: 'dark:bg-green-900 dark:text-green-200',
    label: 'Government',
  },
  Political: {
    icon: Users,
    color: 'bg-orange-100 text-orange-800 border-orange-300',
    darkColor: 'dark:bg-orange-900 dark:text-orange-200',
    label: 'Political',
  },
  Entertainment: {
    icon: Film,
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    darkColor: 'dark:bg-purple-900 dark:text-purple-200',
    label: 'Entertainment',
  },
  Sports: {
    icon: Trophy,
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    darkColor: 'dark:bg-blue-900 dark:text-blue-200',
    label: 'Sports',
  },
  Crime: {
    icon: AlertTriangle,
    color: 'bg-red-100 text-red-800 border-red-300',
    darkColor: 'dark:bg-red-900 dark:text-red-200',
    label: 'Crime/Accident',
  },
  Business: {
    icon: Briefcase,
    color: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    darkColor: 'dark:bg-indigo-900 dark:text-indigo-200',
    label: 'Business',
  },
  Other: {
    icon: HelpCircle,
    color: 'bg-gray-100 text-gray-800 border-gray-300',
    darkColor: 'dark:bg-gray-700 dark:text-gray-200',
    label: 'Other',
  },
};

export default function ClassificationBadge({ 
  category, 
  subCategory, 
  confidence,
  size = 'md' 
}: ClassificationBadgeProps) {
  const config = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG] || CATEGORY_CONFIG.Other;
  const Icon = config.icon;
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };
  
  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  return (
    <div className="flex items-center space-x-2">
      <span
        className={`inline-flex items-center space-x-1.5 rounded-full border font-medium ${config.color} ${config.darkColor} ${sizeClasses[size]}`}
        title={subCategory ? `${config.label}: ${subCategory}` : config.label}
      >
        <Icon className={iconSizes[size]} />
        <span>{config.label}</span>
        {confidence !== undefined && confidence > 0 && (
          <span className="opacity-70 text-xs">
            ({Math.round(confidence * 100)}%)
          </span>
        )}
      </span>
      
      {subCategory && (
        <span className="text-xs text-gray-600 dark:text-gray-400 italic">
          {subCategory}
        </span>
      )}
    </div>
  );
}
