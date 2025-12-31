import { ReactNode } from 'react';
import { cn } from '@/react-app/utils/cn';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  gradient?: boolean;
}

export default function GlassCard({ children, className, hover = true, gradient = false }: GlassCardProps) {
  return (
    <div
      className={cn(
        'relative bg-white dark:bg-gray-900',
        'border border-gray-200 dark:border-gray-700',
        'rounded-2xl shadow-xl',
        'transition-all duration-500',
        hover && 'hover:shadow-2xl hover:scale-[1.02] hover:-translate-y-1',
        gradient && 'before:absolute before:inset-0 before:rounded-2xl before:bg-gradient-to-br before:from-white/40 before:to-transparent before:pointer-events-none',
        className
      )}
    >
      {children}
    </div>
  );
}
