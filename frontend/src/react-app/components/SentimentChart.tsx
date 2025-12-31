import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface SentimentTrend {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
}

interface SentimentChartProps {
  data: SentimentTrend[];
}

export default function SentimentChart({ data }: SentimentChartProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formattedData = data.map(item => ({
    ...item,
    date: formatDate(item.date),
  }));

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Trends (Last 7 Days)</h3>
      {formattedData && formattedData.length > 0 ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="positive" fill="#10b981" name="Positive" />
              <Bar dataKey="neutral" fill="#6b7280" name="Neutral" />
              <Bar dataKey="negative" fill="#ef4444" name="Negative" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-24 flex items-center justify-center text-gray-500">No sentiment data</div>
      )}
    </div>
  );
}
