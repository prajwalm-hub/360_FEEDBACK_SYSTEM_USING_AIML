// PWA registration and offline support utilities

export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);

          // Check for updates periodically
          setInterval(() => {
            registration.update();
          }, 60000); // Check every minute
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });
    });
  }
}

export function unregisterServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.unregister();
    });
  }
}

// Check if app is running in standalone mode (installed PWA)
export function isStandalone(): boolean {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone === true
  );
}

// Request notification permission
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) {
    console.warn('This browser does not support notifications');
    return 'denied';
  }

  const permission = await Notification.requestPermission();
  return permission;
}

// Show notification
export function showNotification(title: string, options?: NotificationOptions) {
  if ('Notification' in window && Notification.permission === 'granted') {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.showNotification(title, {
          icon: '/vite.svg',
          badge: '/vite.svg',
          ...options,
        });
      });
    } else {
      new Notification(title, options);
    }
  }
}

// Background sync for offline data
export async function registerBackgroundSync(tag: string) {
  if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await (registration as any).sync.register(tag);
      console.log('Background sync registered:', tag);
    } catch (error) {
      console.error('Background sync registration failed:', error);
    }
  }
}

// Check online/offline status
export function setupNetworkStatusListener(
  onOnline?: () => void,
  onOffline?: () => void
) {
  window.addEventListener('online', () => {
    console.log('App is online');
    onOnline?.();
  });

  window.addEventListener('offline', () => {
    console.log('App is offline');
    onOffline?.();
  });
}

// Get network status
export function isOnline(): boolean {
  return navigator.onLine;
}

// Cache API wrapper for offline data
export class OfflineCache {
  private cacheName: string;

  constructor(cacheName: string = 'newsscope-data-v1') {
    this.cacheName = cacheName;
  }

  async set(key: string, data: any): Promise<void> {
    try {
      const cache = await caches.open(this.cacheName);
      const response = new Response(JSON.stringify(data));
      await cache.put(key, response);
    } catch (error) {
      console.error('Failed to cache data:', error);
    }
  }

  async get(key: string): Promise<any | null> {
    try {
      const cache = await caches.open(this.cacheName);
      const response = await cache.match(key);
      if (response) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error('Failed to retrieve cached data:', error);
      return null;
    }
  }

  async remove(key: string): Promise<void> {
    try {
      const cache = await caches.open(this.cacheName);
      await cache.delete(key);
    } catch (error) {
      console.error('Failed to remove cached data:', error);
    }
  }

  async clear(): Promise<void> {
    try {
      await caches.delete(this.cacheName);
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }
}

// Install prompt for PWA
let deferredPrompt: any = null;

export function setupInstallPrompt(onInstallReady?: () => void) {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    onInstallReady?.();
  });
}

export async function showInstallPrompt(): Promise<boolean> {
  if (!deferredPrompt) {
    return false;
  }

  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  deferredPrompt = null;

  return outcome === 'accepted';
}

export function canInstallPWA(): boolean {
  return deferredPrompt !== null;
}
