import React from 'react';
import { Languages } from 'lucide-react';

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
  languageStats?: { language: string; language_name: string; count: number }[];
}

const SUPPORTED_LANGUAGES = {
  all: { name: 'All Languages', native: '🌐 All', flag: '🌐' },
  en: { name: 'English', native: 'English', flag: '🇬🇧' },
  hi: { name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  kn: { name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  ta: { name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  te: { name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  bn: { name: 'Bengali', native: 'বাংলা', flag: '🇮🇳' },
  gu: { name: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳' },
  mr: { name: 'Marathi', native: 'मराठी', flag: '🇮🇳' },
  pa: { name: 'Punjabi', native: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  ml: { name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳' },
  or: { name: 'Odia', native: 'ଓଡ଼ିଆ', flag: '🇮🇳' },
  ur: { name: 'Urdu', native: 'اردو', flag: '🇮🇳' },
};

export default function LanguageSelector({ 
  selectedLanguage, 
  onLanguageChange,
  languageStats = []
}: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false);

  const getLanguageCount = (lang: string) => {
    if (lang === 'all') return languageStats.reduce((sum, stat) => sum + stat.count, 0);
    const stat = languageStats.find(s => s.language === lang);
    return stat ? stat.count : 0;
  };

  const currentLang = SUPPORTED_LANGUAGES[selectedLanguage as keyof typeof SUPPORTED_LANGUAGES] || SUPPORTED_LANGUAGES.all;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <Languages className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        <span className="font-medium text-gray-900 dark:text-white">
          {currentLang.flag} {currentLang.native}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-20 max-h-96 overflow-y-auto">
            <div className="p-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Select Language
              </div>
              {Object.entries(SUPPORTED_LANGUAGES).map(([code, lang]) => {
                const count = getLanguageCount(code);
                const isSelected = selectedLanguage === code;
                
                return (
                  <button
                    key={code}
                    onClick={() => {
                      onLanguageChange(code);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                      isSelected
                        ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{lang.flag}</span>
                      <div className="text-left">
                        <div className="font-medium">{lang.native}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">{lang.name}</div>
                      </div>
                    </div>
                    {count > 0 && (
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        isSelected
                          ? 'bg-indigo-100 dark:bg-indigo-800 text-indigo-700 dark:text-indigo-300'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                      }`}>
                        {count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
