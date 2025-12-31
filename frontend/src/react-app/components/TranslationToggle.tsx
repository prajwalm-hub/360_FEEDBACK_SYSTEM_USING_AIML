import { Globe2 } from 'lucide-react';

interface TranslationToggleProps {
  hasTranslation: boolean;
  showTranslation: boolean;
  onToggle: () => void;
  originalLanguage?: string;
}

export default function TranslationToggle({
  hasTranslation,
  showTranslation,
  onToggle,
  originalLanguage,
}: TranslationToggleProps) {
  if (!hasTranslation) return null;

  return (
    <button
      onClick={onToggle}
      className="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors border border-blue-200 dark:border-blue-800"
      title={showTranslation ? 'Show original' : 'Show translation'}
    >
      <Globe2 className="w-4 h-4" />
      <span className="font-medium">
        {showTranslation ? `Original (${originalLanguage})` : 'English Translation'}
      </span>
      <svg
        className={`w-4 h-4 transition-transform ${showTranslation ? 'rotate-180' : ''}`}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
      </svg>
    </button>
  );
}
