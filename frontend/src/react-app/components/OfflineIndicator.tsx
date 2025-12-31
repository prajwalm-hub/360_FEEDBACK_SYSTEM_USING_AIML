import { useState, useEffect } from 'react';
import { Wifi, WifiOff } from 'lucide-react';
import { isOnline, setupNetworkStatusListener } from '@/react-app/utils/pwa';

export default function OfflineIndicator() {
  const [online, setOnline] = useState(isOnline());
  const [showIndicator, setShowIndicator] = useState(false);

  useEffect(() => {
    setupNetworkStatusListener(
      () => {
        setOnline(true);
        setShowIndicator(true);
        setTimeout(() => setShowIndicator(false), 3000);
      },
      () => {
        setOnline(false);
        setShowIndicator(true);
      }
    );

    // Initial check
    setOnline(isOnline());
    if (!isOnline()) {
      setShowIndicator(true);
    }
  }, []);

  if (!showIndicator) {
    return null;
  }

  return (
    <div className="fixed top-20 right-4 z-50 animate-slide-in-right">
      <div className={`glass rounded-xl p-4 shadow-lg border ${
        online 
          ? 'border-green-200 bg-green-50/90' 
          : 'border-orange-200 bg-orange-50/90'
      }`}>
        <div className="flex items-center space-x-3">
          {online ? (
            <>
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <Wifi className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-green-900">Back Online</p>
                <p className="text-sm text-green-700">Connection restored</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center animate-pulse">
                <WifiOff className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-orange-900">Offline Mode</p>
                <p className="text-sm text-orange-700">Working with cached data</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
