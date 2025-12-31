import { useEffect, useRef, useState } from 'react';
import GlassCard from './GlassCard';

interface WordCloudProps {
  words: Array<{ text: string; value: number; color?: string }>;
  width?: number;
  height?: number;
}

export default function WordCloud({ words, width = 800, height = 400 }: WordCloudProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !words.length) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Sort words by value
    const sortedWords = [...words].sort((a, b) => b.value - a.value);
    const maxValue = Math.max(...sortedWords.map(w => w.value));
    const minValue = Math.min(...sortedWords.map(w => w.value));

    // Calculate font sizes
    const maxFontSize = 60;
    const minFontSize = 14;

    const wordsWithPositions: Array<{
      text: string;
      x: number;
      y: number;
      fontSize: number;
      color: string;
      width: number;
      height: number;
    }> = [];

    sortedWords.forEach((word, index) => {
      // Calculate font size based on value
      const fontSize = minFontSize + ((word.value - minValue) / (maxValue - minValue)) * (maxFontSize - minFontSize);
      
      ctx.font = `bold ${fontSize}px Inter, sans-serif`;
      const metrics = ctx.measureText(word.text);
      const wordWidth = metrics.width;
      const wordHeight = fontSize;

      // Try to place word (simple spiral placement)
      let placed = false;
      let attempts = 0;
      const maxAttempts = 100;
      
      let x = width / 2;
      let y = height / 2;
      const angle = index * 0.5;
      const radius = index * 10;

      while (!placed && attempts < maxAttempts) {
        x = width / 2 + Math.cos(angle + attempts * 0.3) * (radius + attempts * 5);
        y = height / 2 + Math.sin(angle + attempts * 0.3) * (radius + attempts * 5);

        // Check collision with existing words
        const collision = wordsWithPositions.some(w => {
          return !(x > w.x + w.width || 
                   x + wordWidth < w.x || 
                   y > w.y + w.height || 
                   y + wordHeight < w.y);
        });

        if (!collision && x >= 0 && x + wordWidth <= width && y >= 0 && y + wordHeight <= height) {
          placed = true;
        }
        attempts++;
      }

      if (placed) {
        const color = word.color || `hsl(${(index * 30) % 360}, 70%, 50%)`;
        wordsWithPositions.push({
          text: word.text,
          x,
          y,
          fontSize,
          color,
          width: wordWidth,
          height: wordHeight,
        });
      }
    });

    // Draw words
    wordsWithPositions.forEach(word => {
      ctx.font = `bold ${word.fontSize}px Inter, sans-serif`;
      ctx.fillStyle = hoveredWord === word.text ? '#3B82F6' : word.color;
      ctx.fillText(word.text, word.x, word.y);
      
      // Add shadow for depth
      ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
      ctx.shadowBlur = 4;
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
    });

  }, [words, width, height, hoveredWord]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Simple hover detection (would need proper word bounds tracking for production)
    setHoveredWord(null);
  };

  return (
    <GlassCard className="p-6">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
          <span>Trending Keywords</span>
        </h3>
        <p className="text-sm text-gray-600 mt-1">Most mentioned terms in recent articles</p>
      </div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseMove={handleMouseMove}
        className="w-full rounded-xl bg-gradient-to-br from-blue-50 to-purple-50 cursor-pointer"
      />
    </GlassCard>
  );
}
