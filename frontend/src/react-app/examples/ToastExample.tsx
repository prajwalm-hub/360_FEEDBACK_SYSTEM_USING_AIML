// Example usage of Toast notifications

import { useToast } from '@/react-app/components/Toast';

export function ExampleComponent() {
  const { showToast } = useToast();

  const handleSuccess = () => {
    showToast('Article saved successfully!', 'success');
  };

  const handleError = () => {
    showToast('Failed to load data. Please try again.', 'error');
  };

  const handleInfo = () => {
    showToast('New articles available. Refresh to see updates.', 'info');
  };

  const handleWarning = () => {
    showToast('Your session will expire in 5 minutes.', 'warning', 10000);
  };

  return (
    <div className="space-x-2">
      <button onClick={handleSuccess}>Show Success</button>
      <button onClick={handleError}>Show Error</button>
      <button onClick={handleInfo}>Show Info</button>
      <button onClick={handleWarning}>Show Warning</button>
    </div>
  );
}

// You can now use showToast() anywhere in your components that are wrapped by ToastProvider:
// showToast('Message here', 'success' | 'error' | 'info' | 'warning', duration_in_ms)
