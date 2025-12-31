import { useState } from 'react';
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps';
import { useNavigate } from 'react-router-dom';

interface StateData {
  state: string;
  totalArticles: number;
  positive: number;
  negative: number;
  neutral: number;
  dominantSentiment: 'positive' | 'negative' | 'neutral';
  sentimentScore: number;
  topHeadline: string;
}

interface IndiaMapProps {
  stateData: { [key: string]: StateData };
}

export default function IndiaMap({ stateData }: IndiaMapProps) {
  const [tooltipContent, setTooltipContent] = useState<string>('');
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const navigate = useNavigate();

  const getSentimentColor = (stateName: string) => {
    const data = stateData[stateName];
    if (!data) return '#d1d5db';

    const { dominantSentiment, sentimentScore } = data;
    const intensity = Math.min(sentimentScore / 100, 1);

    if (dominantSentiment === 'positive') {
      const green = Math.floor(197 + (255 - 197) * (1 - intensity));
      return `rgb(34, ${green}, 94)`;
    }
    if (dominantSentiment === 'negative') {
      const red = Math.floor(68 + (255 - 68) * (1 - intensity));
      return `rgb(239, ${red}, 68)`;
    }
    const blue = Math.floor(130 + (255 - 130) * (1 - intensity));
    return `rgb(59, ${blue}, 246)`;
  };

  const handleMouseEnter = (geo: any, event: React.MouseEvent) => {
    const stateName = geo.properties.name;
    const data = stateData[stateName];

    if (data) {
      const posPercent = ((data.positive / data.totalArticles) * 100).toFixed(0);
      const negPercent = ((data.negative / data.totalArticles) * 100).toFixed(0);
      const neuPercent = ((data.neutral / data.totalArticles) * 100).toFixed(0);

      setTooltipContent(`
        ${stateName}
        Articles: ${data.totalArticles}
        Positive: ${posPercent}% | Neutral: ${neuPercent}% | Negative: ${negPercent}%
        Top: ${data.topHeadline.substring(0, 60)}...
      `);
    } else {
      setTooltipContent(`${stateName}\nNo data available`);
    }

    setTooltipPosition({ x: event.clientX, y: event.clientY });
  };

  const handleMouseLeave = () => {
    setTooltipContent('');
  };

  const handleClick = (geo: any) => {
    const stateName = geo.properties.name;
    if (stateData[stateName]) {
      navigate(`/news-feed?region=${encodeURIComponent(stateName)}`);
    }
  };

  return (
    <div className="relative">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          scale: 1000,
          center: [78.9629, 22.5937]
        }}
        width={800}
        height={600}
        className="w-full h-auto"
      >
        <ZoomableGroup center={[78.9629, 22.5937]} zoom={1}>
          <Geographies geography="/india-states.json">
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={getSentimentColor(geo.properties.name)}
                  stroke="#fff"
                  strokeWidth={0.5}
                  onMouseEnter={(event) => handleMouseEnter(geo, event)}
                  onMouseLeave={handleMouseLeave}
                  onClick={() => handleClick(geo)}
                  style={{
                    default: { outline: 'none' },
                    hover: { fill: '#4f46e5', outline: 'none', cursor: 'pointer' },
                    pressed: { outline: 'none' }
                  }}
                />
              ))
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>

      {tooltipContent && (
        <div
          className="fixed bg-gray-900 text-white text-xs p-3 rounded shadow-lg z-50 max-w-xs pointer-events-none"
          style={{
            left: `${tooltipPosition.x + 10}px`,
            top: `${tooltipPosition.y + 10}px`
          }}
        >
          {tooltipContent.split('\n').map((line, i) => (
            <div key={i} className={i === 0 ? 'font-bold mb-1' : ''}>{line}</div>
          ))}
        </div>
      )}
    </div>
  );
}
