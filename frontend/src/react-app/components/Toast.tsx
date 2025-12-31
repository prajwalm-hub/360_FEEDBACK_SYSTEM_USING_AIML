import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastContextType {
  showToast: (message: string, type: ToastType, duration?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType, duration = 5000) => {
    const id = Math.random().toString(36).substring(7);
    const newToast: Toast = { id, message, type, duration };
    
    setToasts((prev) => [...prev, newToast]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[9999] space-y-2 max-w-md">
        {toasts.map((toast, index) => (
          <ToastItem
            key={toast.id}
            toast={toast}
            onClose={() => removeToast(toast.id)}
            index={index}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onClose, index }: { toast: Toast; onClose: () => void; index: number }) {
  const [progress, setProgress] = useState(100);

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info,
    warning: AlertTriangle,
  };

  const colors = {
    success: {
      bg: 'from-green-500 to-emerald-600',
      icon: 'text-green-100',
      border: 'border-green-400/30',
    },
    error: {
      bg: 'from-red-500 to-pink-600',
      icon: 'text-red-100',
      border: 'border-red-400/30',
    },
    info: {
      bg: 'from-blue-500 to-indigo-600',
      icon: 'text-blue-100',
      border: 'border-blue-400/30',
    },
    warning: {
      bg: 'from-yellow-500 to-orange-600',
      icon: 'text-yellow-100',
      border: 'border-yellow-400/30',
    },
  };

  const Icon = icons[toast.type];
  const color = colors[toast.type];

  // Progress bar animation
  if (toast.duration && toast.duration > 0) {
    setTimeout(() => {
      setProgress(0);
    }, 50);
  }

  return (
    <div
      className="animate-slide-in-right relative"
      style={{
        animationDelay: `${index * 0.1}s`,
      }}
    >
      <div className={`glass border ${color.border} rounded-xl shadow-2xl overflow-hidden min-w-[320px] transform hover:scale-105 transition-transform duration-300`}>
        <div className={`bg-gradient-to-r ${color.bg} p-4`}>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Icon className={`w-6 h-6 ${color.icon}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium text-sm leading-relaxed">
                {toast.message}
              </p>
            </div>
            <button
              onClick={onClose}
              className="flex-shrink-0 text-white/80 hover:text-white transition-colors hover:rotate-90 transform duration-300"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        {toast.duration && toast.duration > 0 && (
          <div className="h-1 bg-white/20">
            <div
              className="h-full bg-white/60 transition-all ease-linear"
              style={{
                width: `${progress}%`,
                transitionDuration: `${toast.duration}ms`,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

// CSS for slide-in animation (add to index.css if not already there)
const styles = `
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.3s ease-out;
}
`;
