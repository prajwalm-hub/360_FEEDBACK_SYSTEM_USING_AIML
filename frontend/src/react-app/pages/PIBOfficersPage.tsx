import { useState } from 'react';
import { useApi, apiCall } from '@/react-app/hooks/useApi';
import { useAuth } from '@/react-app/context/AuthContext';
import PIBOfficerCard from '@/react-app/components/PIBOfficerCard';
import LoadingSpinner from '@/react-app/components/LoadingSpinner';
import EmptyState from '@/react-app/components/EmptyState';
import { PIBOfficer } from '@/shared/types';
import { Users, Plus, RefreshCw, Mail, Phone, ShieldAlert } from 'lucide-react';

export default function PIBOfficersPage() {
  const { isAdmin } = useAuth();
  const { data: officers, loading, error, refetch } = useApi<PIBOfficer[]>('/pib-officers');
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [newOfficer, setNewOfficer] = useState({
    name: '',
    email: '',
    phone: '',
    department: '',
  });

  // If not admin, show access denied
  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ShieldAlert className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600">You don't have permission to access this page.</p>
          <p className="text-sm text-gray-500 mt-2">Only administrators can manage PIB Officers.</p>
        </div>
      </div>
    );
  }

  const handleToggleStatus = async (officerId: number) => {
    try {
      await apiCall(`/pib-officers/${officerId}/toggle-status`, { method: 'POST' });
      window.location.reload();
    } catch (error) {
      console.error('Failed to toggle officer status:', error);
    }
  };

  const handleAddOfficer = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    
    try {
      const result = await apiCall('/pib-officers', {
        method: 'POST',
        body: JSON.stringify(newOfficer),
      });
      
      console.log('Officer added successfully:', result);
      
      // Reset form and close
      setNewOfficer({ name: '', email: '', phone: '', department: '' });
      setShowAddForm(false);
      
      // Refresh the list
      refetch();
      
      // Show success message (you can add a toast notification here)
      alert('PIB Officer added successfully!');
    } catch (error) {
      console.error('Failed to add officer:', error);
      setFormError(error instanceof Error ? error.message : 'Failed to add officer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Users className="w-8 h-8 mr-3 text-blue-600" />
            PIB Officers Management
          </h1>
          <p className="text-gray-600 mt-1">Manage PIB officers who receive alert notifications</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Officer</span>
          </button>
          <button
            onClick={handleRefresh}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Add Officer Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New PIB Officer</h3>
          <form onSubmit={handleAddOfficer} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input
                type="text"
                required
                value={newOfficer.name}
                onChange={(e) => setNewOfficer(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Officer's full name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="email"
                  required
                  value={newOfficer.email}
                  onChange={(e) => setNewOfficer(prev => ({ ...prev, email: e.target.value }))}
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="officer@pib.gov.in"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="tel"
                  value={newOfficer.phone}
                  onChange={(e) => setNewOfficer(prev => ({ ...prev, phone: e.target.value }))}
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="+91-9876543210"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <input
                type="text"
                value={newOfficer.department}
                onChange={(e) => setNewOfficer(prev => ({ ...prev, department: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Information & Broadcasting"
              />
            </div>

            <div className="md:col-span-2">
              {formError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                  {formError}
                </div>
              )}
              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={submitting}
                  className={`px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 ${
                    submitting ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {submitting ? (
                    <>
                      <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Adding...</span>
                    </>
                  ) : (
                    <span>Add Officer</span>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddForm(false);
                    setFormError(null);
                  }}
                  disabled={submitting}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Officers List */}
      {loading ? (
        <LoadingSpinner message="Loading PIB officers..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-medium">Error loading PIB officers</h3>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      ) : !officers || officers.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No PIB officers found"
          description="Add PIB officers to start receiving alert notifications for important government news."
          action={{
            label: "Add First Officer",
            onClick: () => setShowAddForm(true)
          }}
        />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-blue-50 px-4 py-3 rounded-lg border border-blue-200">
            <span className="text-sm font-medium text-blue-900">
              {officers.length} PIB Officer{officers.length !== 1 ? 's' : ''} registered
            </span>
            <span className="text-xs text-blue-700">
              {officers.filter(o => o.is_active).length} active
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {officers.map((officer) => (
              <PIBOfficerCard 
                key={officer.id} 
                officer={officer} 
                onToggleStatus={handleToggleStatus}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
