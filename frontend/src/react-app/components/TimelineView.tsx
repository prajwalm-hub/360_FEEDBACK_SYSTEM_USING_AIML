import { Line } from 'recharts';
import { LineChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import GlassCard from './GlassCard';
import { TrendingUp, Calendar } from 'lucide-react';

interface TimelineData {
  date: string;
  articles: number;
  sentiment: number;
  positive: number;
  negative: number;
  neutral: number;
}

interface TimelineViewProps {
  data: TimelineData[];
}

export default function TimelineView({ data }: TimelineViewProps) {
  return (
    <GlassCard className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-blue-500" />
              <span>News Timeline</span>
            </h3>
            <p className="text-sm text-gray-600 mt-1">Article volume and sentiment trends over time</p>
          </div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-green-500 animate-pulse" />
            <span className="text-sm font-medium text-gray-700">Live Tracking</span>
          </div>
        </div>
      </div>

      {/* Article Volume Timeline */}
      <div className="mb-8">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Article Volume</h4>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorArticles" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="date" 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '12px',
              }}
            />
            <Area 
              type="monotone" 
              dataKey="articles" 
              stroke="#3B82F6" 
              fillOpacity={1} 
              fill="url(#colorArticles)"
              strokeWidth={2}
              animationDuration={1500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Sentiment Timeline */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Sentiment Distribution</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="date" 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '12px',
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }}
            />
            <Line 
              type="monotone" 
              dataKey="positive" 
              stroke="#10B981" 
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              animationDuration={1500}
            />
            <Line 
              type="monotone" 
              dataKey="neutral" 
              stroke="#6B7280" 
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              animationDuration={1500}
              animationBegin={200}
            />
            <Line 
              type="monotone" 
              dataKey="negative" 
              stroke="#EF4444" 
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              animationDuration={1500}
              animationBegin={400}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
