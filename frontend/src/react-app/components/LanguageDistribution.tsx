import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface LanguageData {
  language: string;
  count: number;
}

interface LanguageDistributionProps {
  data: LanguageData[];
}

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1',
  '#14b8a6', '#a855f7'
];

const LANGUAGE_INFO: Record<string, { native: string; flag: string }> = {
  'hindi': { native: 'हिन्दी', flag: '🇮🇳' },
  'kannada': { native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  'tamil': { native: 'தமிழ்', flag: '🇮🇳' },
  'telugu': { native: 'తెలుగు', flag: '🇮🇳' },
  'bengali': { native: 'বাংলা', flag: '🇮🇳' },
  'gujarati': { native: 'ગુજરાતી', flag: '🇮🇳' },
  'marathi': { native: 'मराठी', flag: '🇮🇳' },
  'punjabi': { native: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  'malayalam': { native: 'മലയാളം', flag: '🇮🇳' },
  'odia': { native: 'ଓଡ଼ିଆ', flag: '🇮🇳' },
  'urdu': { native: 'اردو', flag: '🇮🇳' },
  'english': { native: 'English', flag: '🇬🇧' },
};

export default function LanguageDistribution({ data }: LanguageDistributionProps) {
  const total = data.reduce((sum, item) => sum + item.count, 0);

  const formattedData = data.map((item, index) => ({
    ...item,
    color: COLORS[index % COLORS.length],
    percentage: ((item.count / total) * 100).toFixed(1),
    nativeName: LANGUAGE_INFO[item.language.toLowerCase()]?.native || item.language,
    flag: LANGUAGE_INFO[item.language.toLowerCase()]?.flag || '🌐',
  }));

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage }: any) => {
    if (parseFloat(percentage) < 5) return null; // Don't show label for small slices
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize="12" fontWeight="bold">
        {`${percentage}%`}
      </text>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Language Distribution</h3>
      {total > 0 ? (
        <div className="flex flex-col lg:flex-row items-center">
          <div className="h-64 w-full lg:w-2/3">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={formattedData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomizedLabel}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {formattedData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [value, 'Articles']}
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem' }}
                  labelStyle={{ color: '#f3f4f6' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="w-full lg:w-1/3 mt-4 lg:mt-0">
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {formattedData.map((item) => (
                <div key={item.language} className="flex items-center justify-between text-sm py-1">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-lg" role="img" aria-label={item.language}>
                      {item.flag}
                    </span>
                    <span className="text-gray-700 dark:text-gray-300 font-medium">
                      {item.nativeName}
                    </span>
                  </div>
                  <div className="text-gray-900 dark:text-white font-semibold">
                    {item.count} <span className="text-gray-500 dark:text-gray-400 text-xs">({item.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="h-24 flex items-center justify-center text-gray-500">No language data</div>
      )}
    </div>
  );
}
