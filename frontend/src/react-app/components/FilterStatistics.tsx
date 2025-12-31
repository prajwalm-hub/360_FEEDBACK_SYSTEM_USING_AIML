import { Eye, EyeOff, BarChart3, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface FilterStatisticsProps {
  total: number;
  shown: number;
  filtered: number;
  byCategory: Array<{ category: string; count: number }>;
  filteredBreakdown: Array<{ category: string; count: number }>;
}

export default function FilterStatistics({
  total,
  shown,
  filtered,
  byCategory,
  filteredBreakdown,
}: FilterStatisticsProps) {
  const [expanded, setExpanded] = useState(false);

  const shownPercentage = total > 0 ? Math.round((shown / total) * 100) : 0;
  const filteredPercentage = total > 0 ? Math.round((filtered / total) * 100) : 0;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-lg border border-blue-200 dark:border-gray-600 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="font-semibold text-gray-900 dark:text-white">
              Content Filter Statistics
            </span>
          </div>
          
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 px-3 py-1.5 rounded-full border border-green-300 dark:border-green-700">
              <Eye className="w-4 h-4 text-green-600 dark:text-green-400" />
              <span className="font-medium text-green-900 dark:text-green-200">
                Showing: {shown.toLocaleString()}
              </span>
              <span className="text-xs text-green-700 dark:text-green-400">
                ({shownPercentage}%)
              </span>
            </div>
            
            <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 px-3 py-1.5 rounded-full border border-red-300 dark:border-red-700">
              <EyeOff className="w-4 h-4 text-red-600 dark:text-red-400" />
              <span className="font-medium text-red-900 dark:text-red-200">
                Filtered: {filtered.toLocaleString()}
              </span>
              <span className="text-xs text-red-700 dark:text-red-400">
                ({filteredPercentage}%)
              </span>
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center space-x-1 text-sm text-blue-700 dark:text-blue-300 hover:text-blue-900 dark:hover:text-blue-100 transition-colors"
        >
          <span>{expanded ? 'Hide Details' : 'Show Details'}</span>
          {expanded ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </button>
      </div>
      
      {expanded && (
        <div className="mt-4 pt-4 border-t border-blue-200 dark:border-gray-600">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* All Categories */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                All Content by Category
              </h4>
              <div className="space-y-1">
                {byCategory.map((item) => (
                  <div
                    key={item.category}
                    className="flex items-center justify-between text-sm bg-white dark:bg-gray-800 px-3 py-1.5 rounded"
                  >
                    <span className="text-gray-700 dark:text-gray-300">{item.category}</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {item.count.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Filtered Breakdown */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Filtered Content (Hidden from PIB Officers)
              </h4>
              {filteredBreakdown.length > 0 ? (
                <div className="space-y-1">
                  {filteredBreakdown.map((item) => (
                    <div
                      key={item.category}
                      className="flex items-center justify-between text-sm bg-red-50 dark:bg-red-900/20 px-3 py-1.5 rounded border border-red-200 dark:border-red-800"
                    >
                      <span className="text-red-700 dark:text-red-300">{item.category}</span>
                      <span className="font-medium text-red-900 dark:text-red-200">
                        {item.count.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  No content filtered
                </p>
              )}
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg border border-blue-300 dark:border-blue-700">
            <p className="text-xs text-blue-900 dark:text-blue-200">
              <strong>Note:</strong> PIB Officer Mode shows only Government-related content (schemes, policies, services, infrastructure, public grievances, and misinformation alerts). Political party activities, entertainment, sports, and other non-government content are automatically filtered out to prevent misuse.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
