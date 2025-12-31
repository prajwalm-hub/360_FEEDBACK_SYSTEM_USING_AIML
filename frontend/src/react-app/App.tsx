import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import { AuthProvider, useAuth } from "@/react-app/context/AuthContext";
import { ToastProvider } from "@/react-app/components/Toast";
import HomePage from "@/react-app/pages/Home";
import ModernLoginPage from "@/react-app/pages/ModernLoginPage";
import GeographicView from "@/react-app/pages/GeographicView";
import AssistantPage from "@/react-app/pages/AssistantPage";
import InstallPWABanner from "@/react-app/components/InstallPWABanner";
import OfflineIndicator from "@/react-app/components/OfflineIndicator";

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Redirect authenticated users from login page to dashboard
  useEffect(() => {
    if (isAuthenticated && window.location.pathname === '/login') {
      window.location.href = '/';
    }
  }, [isAuthenticated]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
      <Route path="/login" element={<ModernLoginPage />} />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/geographic" 
        element={
          <ProtectedRoute>
            <GeographicView />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/articles" 
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/assistant" 
        element={
          <ProtectedRoute>
            <AssistantPage />
          </ProtectedRoute>
        } 
      />
      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <Router>
          <AppRoutes />
          <InstallPWABanner />
          <OfflineIndicator />
        </Router>
      </AuthProvider>
    </ToastProvider>
  );
}
