import { useState, useEffect } from 'react';
import { X, Download, Smartphone } from 'lucide-react';
import { canInstallPWA, showInstallPrompt, setupInstallPrompt, isStandalone } from '@/react-app/utils/pwa';

export default function InstallPWABanner() {
  const [showBanner, setShowBanner] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);

  useEffect(() => {
    // Don't show if already installed
    if (isStandalone()) {
      return;
    }

    // Setup install prompt listener
    setupInstallPrompt(() => {
      // Check if user has dismissed banner before
      const dismissed = localStorage.getItem('pwa-banner-dismissed');
      if (!dismissed) {
        setShowBanner(true);
      }
    });

    // Show banner if install is available
    if (canInstallPWA()) {
      const dismissed = localStorage.getItem('pwa-banner-dismissed');
      if (!dismissed) {
        setShowBanner(true);
      }
    }
  }, []);

  const handleInstall = async () => {
    setIsInstalling(true);
    const accepted = await showInstallPrompt();
    
    if (accepted) {
      setShowBanner(false);
      localStorage.setItem('pwa-installed', 'true');
    }
    setIsInstalling(false);
  };

  const handleDismiss = () => {
    setShowBanner(false);
    localStorage.setItem('pwa-banner-dismissed', 'true');
  };

  if (!showBanner) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 animate-slide-in-bottom">
      <div className="max-w-4xl mx-auto m-4">
        <div className="rounded-2xl p-4 shadow-2xl border border-white/20 bg-gradient-to-r from-blue-500 to-purple-600">\n          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-lg">
                <Smartphone className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-bold text-white text-lg">Install NewsScope India</h3>
                <p className="text-blue-100 text-sm">Get instant access and work offline</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleInstall}
                disabled={isInstalling}
                className="flex items-center space-x-2 px-6 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-all duration-300 hover:scale-105 disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                <span>{isInstalling ? 'Installing...' : 'Install'}</span>
              </button>
              <button
                onClick={handleDismiss}
                className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
