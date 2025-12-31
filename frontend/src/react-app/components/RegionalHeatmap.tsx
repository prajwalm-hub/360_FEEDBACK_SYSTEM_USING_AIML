import { useEffect, useState } from 'react';
import GlassCard from './GlassCard';
import { MapPin } from 'lucide-react';

interface HeatmapData {
  region: string;
  hour: number;
  count: number;
}

interface RegionalHeatmapProps {
  data: HeatmapData[];
}

const REGIONS = [
  'Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal',
  'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Telangana', 'Kerala',
  'Punjab', 'Haryana', 'Madhya Pradesh', 'Andhra Pradesh', 'Odisha'
];

const HOURS = Array.from({ length: 24 }, (_, i) => i);

export default function RegionalHeatmap({ data }: RegionalHeatmapProps) {
  const [maxCount, setMaxCount] = useState(0);

  useEffect(() => {
    const max = Math.max(...data.map(d => d.count), 1);
    setMaxCount(max);
  }, [data]);

  const getColor = (count: number) => {
    if (count === 0) return 'rgba(229, 231, 235, 0.3)'; // gray-200
    const intensity = count / maxCount;
    if (intensity > 0.75) return 'rgba(239, 68, 68, 0.9)'; // red-500
    if (intensity > 0.5) return 'rgba(251, 146, 60, 0.8)'; // orange-400
    if (intensity > 0.25) return 'rgba(250, 204, 21, 0.7)'; // yellow-400
    return 'rgba(134, 239, 172, 0.6)'; // green-300
  };

  const getCellData = (region: string, hour: number) => {
    const cell = data.find(d => d.region === region && d.hour === hour);
    return cell ? cell.count : 0;
  };

  return (
    <GlassCard className="p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
          <MapPin className="w-5 h-5 text-blue-500" />
          <span>Regional Activity Heatmap</span>
        </h3>
        <p className="text-sm text-gray-600 mt-1">News distribution by region and time of day</p>
      </div>

      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Hour Labels */}
          <div className="flex mb-2">
            <div className="w-32 flex-shrink-0"></div>
            {HOURS.map(hour => (
              <div
                key={hour}
                className="flex-shrink-0 w-8 text-xs text-center text-gray-600 font-medium"
              >
                {hour.toString().padStart(2, '0')}
              </div>
            ))}
          </div>

          {/* Heatmap Grid */}
          {REGIONS.map((region, regionIndex) => (
            <div
              key={region}
              className="flex mb-1 animate-fade-in-up"
              style={{ animationDelay: `${regionIndex * 0.05}s` }}
            >
              {/* Region Label */}
              <div className="w-32 flex-shrink-0 pr-2 flex items-center">
                <span className="text-xs font-medium text-gray-700 truncate">
                  {region}
                </span>
              </div>

              {/* Hour Cells */}
              {HOURS.map(hour => {
                const count = getCellData(region, hour);
                return (
                  <div
                    key={hour}
                    className="group relative flex-shrink-0 w-8 h-8 rounded transition-all duration-300 hover:scale-110 cursor-pointer"
                    style={{ backgroundColor: getColor(count) }}
                  >
                    {/* Tooltip */}
                    {count > 0 && (
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                        {region}: {count} articles at {hour}:00
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center justify-center space-x-4">
        <span className="text-xs text-gray-600">Low</span>
        <div className="flex space-x-1">
          {[
            'rgba(134, 239, 172, 0.6)',
            'rgba(250, 204, 21, 0.7)',
            'rgba(251, 146, 60, 0.8)',
            'rgba(239, 68, 68, 0.9)'
          ].map((color, i) => (
            <div
              key={i}
              className="w-6 h-6 rounded"
              style={{ backgroundColor: color }}
            />
          ))}
        </div>
        <span className="text-xs text-gray-600">High</span>
      </div>
    </GlassCard>
  );
}
