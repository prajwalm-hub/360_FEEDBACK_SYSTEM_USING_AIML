import React from 'react';
import RAGAssistant from '../components/RAGAssistant';

const AssistantPage: React.FC = () => {
  const [language] = React.useState<string>('en');

  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1">
        <RAGAssistant 
          apiBaseUrl="/api" 
          language={language}
        />
      </div>
    </div>
  );
};

export default AssistantPage;
