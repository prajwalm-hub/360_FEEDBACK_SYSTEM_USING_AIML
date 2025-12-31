import { Mail, Phone, Building, User, CheckCircle, XCircle } from 'lucide-react';
import { PIBOfficer } from '@/shared/types';

interface PIBOfficerCardProps {
  officer: PIBOfficer;
  onToggleStatus: (officerId: number) => void;
}

export default function PIBOfficerCard({ officer, onToggleStatus }: PIBOfficerCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{officer.name}</h3>
            <p className="text-sm text-gray-600 flex items-center mt-1">
              <Building className="w-4 h-4 mr-1" />
              {officer.department || 'No Department'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            officer.is_active 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {officer.is_active ? (
              <>
                <CheckCircle className="w-3 h-3 mr-1" />
                Active
              </>
            ) : (
              <>
                <XCircle className="w-3 h-3 mr-1" />
                Inactive
              </>
            )}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center space-x-2 text-sm">
          <Mail className="w-4 h-4 text-gray-400" />
          <a 
            href={`mailto:${officer.email}`}
            className="text-blue-600 hover:text-blue-800 transition-colors"
          >
            {officer.email}
          </a>
        </div>
        
        {officer.phone && (
          <div className="flex items-center space-x-2 text-sm">
            <Phone className="w-4 h-4 text-gray-400" />
            <a 
              href={`tel:${officer.phone}`}
              className="text-blue-600 hover:text-blue-800 transition-colors"
            >
              {officer.phone}
            </a>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <button
          onClick={() => onToggleStatus(officer.id)}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
            officer.is_active
              ? 'bg-red-50 text-red-700 hover:bg-red-100'
              : 'bg-green-50 text-green-700 hover:bg-green-100'
          }`}
        >
          {officer.is_active ? 'Deactivate' : 'Activate'}
        </button>
      </div>
    </div>
  );
}
