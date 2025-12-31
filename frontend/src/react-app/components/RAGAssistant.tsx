import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, BookOpen, TrendingUp, History, Trash2, Download, Plus, MessageSquare, Clock, Zap, BarChart3, Lightbulb, Search, Brain, Target, Shield, Globe, Award, Users, Calendar, Briefcase, DollarSign, Heart, Home, School, Leaf, Building2, ChevronRight, Star, Activity } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  confidence?: number;
  timestamp: Date;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

interface Source {
  id: string;
  title: string;
  url: string;
  source: string;
  published_at?: string;
  language: string;
  sentiment?: string;
  is_goi?: boolean;
}

interface RAGAssistantProps {
  apiBaseUrl?: string;
  language?: string;
}

const RAGAssistant: React.FC<RAGAssistantProps> = ({ 
  apiBaseUrl = '/api',
  language = 'en'
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [quickInsights, setQuickInsights] = useState<any>(null);
  const [ragStatus, setRagStatus] = useState<any>(null);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadSuggestions();
    loadQuickInsights();
    checkRagStatus();
    loadChatSessions();
  }, [language]);

  useEffect(() => {
    saveChatSessions();
  }, [chatSessions]);

  const checkRagStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${apiBaseUrl}/rag/status`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setRagStatus(data);
      
      // Auto-build if not initialized
      if (data && !data.initialized) {
        await buildVectorStore();
      }
    } catch (error) {
      console.error('Failed to check RAG status:', error);
      setRagStatus({ initialized: false, error: true });
    }
  };

  const buildVectorStore = async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${apiBaseUrl}/rag/build`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          days: 30,
          force_rebuild: false
        })
      });
    } catch (error) {
      console.error('Failed to build vector store:', error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${apiBaseUrl}/rag/suggestions?language=${language}`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setSuggestions(data?.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      setSuggestions([]);
    }
  };

  const loadQuickInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${apiBaseUrl}/rag/quick-insights?days=7`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setQuickInsights(data);
    } catch (error) {
      console.error('Failed to load quick insights:', error);
      setQuickInsights(null);
    }
  };

  const sendQuery = async (question: string) => {
    if (!question.trim()) return;

    console.log('[RAG Assistant] Sending query:', question);

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: question,
      timestamp: new Date()
    };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    updateCurrentSession(newMessages);
    setInputValue('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const url = `${apiBaseUrl}/rag/query`;
      console.log('[RAG Assistant] Calling API:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question,
          language,
          k: 5
        })
      });

      console.log('[RAG Assistant] Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[RAG Assistant] API error:', errorText);
        throw new Error(`API returned ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('[RAG Assistant] Response data:', data);

      // Add assistant response
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: data?.answer || 'No response received.',
        sources: data?.sources || [],
        confidence: data?.confidence,
        timestamp: new Date()
      };
      const updatedMessages = [...newMessages, assistantMessage];
      setMessages(updatedMessages);
      updateCurrentSession(updatedMessages);
    } catch (error: any) {
      console.error('[RAG Assistant] Error:', error);
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `Error: ${error.message || 'Sorry, I encountered an error processing your question.'}`,
        timestamp: new Date()
      };
      const errorMessages = [...newMessages, errorMessage];
      setMessages(errorMessages);
      updateCurrentSession(errorMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendQuery(inputValue);
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendQuery(suggestion);
  };

  const loadChatSessions = () => {
    const saved = localStorage.getItem('rag_chat_sessions');
    if (saved) {
      try {
        const sessions = JSON.parse(saved).map((s: any) => ({
          ...s,
          createdAt: new Date(s.createdAt),
          updatedAt: new Date(s.updatedAt),
          messages: s.messages.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) }))
        }));
        setChatSessions(sessions);
      } catch (e) {
        console.error('Failed to load chat sessions:', e);
      }
    }
  };

  const saveChatSessions = () => {
    localStorage.setItem('rag_chat_sessions', JSON.stringify(chatSessions));
  };

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}`,
      title: `Chat ${chatSessions.length + 1}`,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setChatSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    setMessages([]);
    setShowHistory(false);
  };

  const loadSession = (sessionId: string) => {
    const session = chatSessions.find(s => s.id === sessionId);
    if (session) {
      setMessages(session.messages);
      setCurrentSessionId(sessionId);
      setShowHistory(false);
    }
  };

  const deleteSession = (sessionId: string) => {
    setChatSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      setMessages([]);
      setCurrentSessionId(null);
    }
  };

  const updateCurrentSession = (newMessages: Message[]) => {
    if (!currentSessionId) {
      // Create new session if none exists
      const newSession: ChatSession = {
        id: `session-${Date.now()}`,
        title: newMessages[0]?.content.slice(0, 50) || 'New Chat',
        messages: newMessages,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      setChatSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
    } else {
      setChatSessions(prev => prev.map(session => 
        session.id === currentSessionId
          ? { 
              ...session, 
              messages: newMessages,
              updatedAt: new Date(),
              title: session.title === `Chat ${chatSessions.length}` && newMessages.length > 0
                ? newMessages[0].content.slice(0, 50)
                : session.title
            }
          : session
      ));
    }
  };

  const exportChat = () => {
    const session = chatSessions.find(s => s.id === currentSessionId);
    if (!session) return;

    const content = session.messages.map(m => 
      `[${m.timestamp.toLocaleString()}] ${m.type.toUpperCase()}: ${m.content}`
    ).join('\n\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${session.title.replace(/[^a-z0-9]/gi, '-')}-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearCurrentChat = () => {
    if (confirm('Clear current chat?')) {
      setMessages([]);
      setCurrentSessionId(null);
    }
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Sidebar - Chat History */}
      {showHistory && (
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <History className="w-4 h-4 mr-2" />
                {language === 'hi' ? 'चैट इतिहास' : 'Chat History'}
              </h3>
              <button
                onClick={() => setShowHistory(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <button
              onClick={createNewSession}
              className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span className="text-sm">{language === 'hi' ? 'नई चैट' : 'New Chat'}</span>
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2">
            {chatSessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-sm">
                {language === 'hi' ? 'कोई चैट इतिहास नहीं' : 'No chat history'}
              </div>
            ) : (
              <div className="space-y-1">
                {chatSessions.map(session => (
                  <div
                    key={session.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      currentSessionId === session.id
                        ? 'bg-indigo-50 border border-indigo-200'
                        : 'hover:bg-gray-50 border border-transparent'
                    }`}
                  >
                    <div className="flex items-start justify-between" onClick={() => loadSession(session.id)}>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <MessageSquare className="w-3 h-3 text-gray-400 flex-shrink-0" />
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {session.title}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2 text-xs text-gray-500">
                          <Clock className="w-3 h-3" />
                          <span>{session.updatedAt.toLocaleDateString()}</span>
                          <span>•</span>
                          <span>{session.messages.length} msgs</span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.id);
                        }}
                        className="ml-2 text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title={language === 'hi' ? 'चैट इतिहास' : 'Chat History'}
              >
                <History className="w-5 h-5 text-gray-600" />
              </button>
              <Sparkles className="w-6 h-6 text-indigo-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {language === 'hi' ? 'समाचार सहायक' : 'News Assistant'}
                </h2>
                <p className="text-sm text-gray-500">
                  {language === 'hi' 
                    ? 'सरकारी समाचारों के बारे में प्रश्न पूछें' 
                    : 'Ask questions about government news'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {messages.length > 0 && (
                <>
                  <button
                    onClick={exportChat}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title={language === 'hi' ? 'चैट निर्यात करें' : 'Export Chat'}
                  >
                    <Download className="w-5 h-5 text-gray-600" />
                  </button>
                  <button
                    onClick={clearCurrentChat}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title={language === 'hi' ? 'चैट साफ़ करें' : 'Clear Chat'}
                  >
                    <Trash2 className="w-5 h-5 text-gray-600" />
                  </button>
                </>
              )}
              {ragStatus && (
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  ragStatus.initialized ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {ragStatus.initialized ? '● Ready' : '● Building...'}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-slate-50 via-white to-blue-50">
        {messages.length === 0 && (
          <div className="max-w-6xl mx-auto">
            {/* Hero Section with Background Pattern */}
            <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 rounded-2xl p-8 mb-6 shadow-xl">
              {/* Animated Background Pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-0 left-0 w-48 h-48 bg-white rounded-full mix-blend-overlay filter blur-3xl animate-pulse"></div>
                <div className="absolute bottom-0 right-0 w-48 h-48 bg-white rounded-full mix-blend-overlay filter blur-3xl animate-pulse delay-1000"></div>
              </div>
              
              <div className="relative z-10 text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl mb-4 shadow-lg">
                  <Sparkles className="w-8 h-8 text-white animate-pulse" />
                </div>
                <h1 className="text-3xl font-bold text-white mb-3 tracking-tight">
                  {language === 'hi' ? 'AI न्यूज़ असिस्टेंट' : 'AI News Assistant'}
                </h1>
                <p className="text-lg text-white/90 mb-4 max-w-2xl mx-auto">
                  {language === 'hi' 
                    ? 'भारत सरकार की नवीनतम नीतियों और समाचारों के बारे में तुरंत जानकारी प्राप्त करें' 
                    : 'Get instant insights from India\'s latest government policies and news'}
                </p>
                <div className="flex items-center justify-center space-x-4 text-white/80 text-xs">
                  <div className="flex items-center">
                    <Activity className="w-3 h-3 mr-1.5" />
                    <span>Real-time Updates</span>
                  </div>
                  <div className="w-1 h-1 bg-white/50 rounded-full"></div>
                  <div className="flex items-center">
                    <Star className="w-3 h-3 mr-1.5" />
                    <span>AI-Powered</span>
                  </div>
                  <div className="w-1 h-1 bg-white/50 rounded-full"></div>
                  <div className="flex items-center">
                    <Shield className="w-3 h-3 mr-1.5" />
                    <span>Verified Sources</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Features Grid */}
            <div className="grid grid-cols-4 gap-3 mb-6">
              {[
                { icon: Brain, title: 'AI-Powered', desc: 'Advanced RAG', gradient: 'from-blue-500 to-cyan-500', iconBg: 'bg-blue-50', iconColor: 'text-blue-600' },
                { icon: Globe, title: 'Multi-Language', desc: '12 Languages', gradient: 'from-green-500 to-emerald-500', iconBg: 'bg-green-50', iconColor: 'text-green-600' },
                { icon: Zap, title: 'Real-time', desc: 'Live Updates', gradient: 'from-yellow-500 to-orange-500', iconBg: 'bg-yellow-50', iconColor: 'text-yellow-600' },
                { icon: Shield, title: 'Verified', desc: 'Trusted Sources', gradient: 'from-purple-500 to-pink-500', iconBg: 'bg-purple-50', iconColor: 'text-purple-600' }
              ].map((feature, idx) => {
                const IconComponent = feature.icon;
                return (
                  <div key={idx} className="group bg-white p-4 rounded-xl shadow hover:shadow-lg transition-all duration-300 border border-gray-100 hover:border-gray-200 cursor-pointer transform hover:-translate-y-0.5">
                    <div className={`w-10 h-10 ${feature.iconBg} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                      <IconComponent className={`w-5 h-5 ${feature.iconColor}`} />
                    </div>
                    <h4 className="font-bold text-gray-900 mb-1 text-sm">{feature.title}</h4>
                    <p className="text-xs text-gray-500">{feature.desc}</p>
                  </div>
                );
              })}
            </div>

            {/* Popular Topics */}
            <div className="bg-white rounded-xl shadow p-5 mb-5 border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                  <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center mr-2">
                    <TrendingUp className="w-4 h-4 text-white" />
                  </div>
                  {language === 'hi' ? 'लोकप्रिय विषय' : 'Popular Topics'}
                </h3>
                <span className="text-xs text-gray-500">Click to explore</span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { icon: Briefcase, title: language === 'hi' ? 'रोजगार योजनाएं' : 'Employment Schemes', count: '156', color: 'blue', gradient: 'from-blue-500 to-cyan-500' },
                  { icon: Heart, title: language === 'hi' ? 'स्वास्थ्य नीतियां' : 'Healthcare Policies', count: '243', color: 'red', gradient: 'from-red-500 to-pink-500' },
                  { icon: School, title: language === 'hi' ? 'शिक्षा योजनाएं' : 'Education Schemes', count: '198', color: 'green', gradient: 'from-green-500 to-emerald-500' },
                  { icon: Home, title: language === 'hi' ? 'आवास योजनाएं' : 'Housing Schemes', count: '127', color: 'orange', gradient: 'from-orange-500 to-yellow-500' },
                  { icon: Leaf, title: language === 'hi' ? 'कृषि नीतियां' : 'Agriculture Policies', count: '289', color: 'teal', gradient: 'from-teal-500 to-green-500' },
                  { icon: Building2, title: language === 'hi' ? 'बुनियादी ढांचा' : 'Infrastructure', count: '165', color: 'purple', gradient: 'from-purple-500 to-indigo-500' }
                ].map((topic, idx) => {
                  const IconComponent = topic.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(`What are the latest ${topic.title} announced?`)}
                      className="group relative bg-gradient-to-br from-gray-50 to-white p-4 rounded-lg border border-gray-100 hover:border-transparent hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5"
                    >
                      <div className={`absolute inset-0 bg-gradient-to-br ${topic.gradient} opacity-0 group-hover:opacity-5 rounded-lg transition-opacity`}></div>
                      <div className="relative">
                        <div className={`w-10 h-10 bg-gradient-to-br ${topic.gradient} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow`}>
                          <IconComponent className="w-5 h-5 text-white" />
                        </div>
                        <h4 className="font-semibold text-gray-900 mb-1.5 text-left text-sm">{topic.title}</h4>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">{topic.count} articles</span>
                          <ChevronRight className="w-3 h-3 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Sample Questions */}
            <div className="bg-white rounded-xl shadow p-5 border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center mr-2">
                  <Lightbulb className="w-4 h-4 text-white" />
                </div>
                {language === 'hi' ? 'सुझाए गए प्रश्न' : 'Suggested Questions'}
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { 
                    icon: Users, 
                    text: language === 'hi' ? 'प्रधानमंत्री के बारे में आज की खबर का सारांश दें' : 'Summarize today\'s news about the Prime Minister', 
                    gradient: 'from-blue-500 to-indigo-600',
                    category: 'Government'
                  },
                  { 
                    icon: Award, 
                    text: language === 'hi' ? 'नवीनतम सरकारी योजनाएं क्या घोषित की गईं?' : 'What are the latest government schemes announced?', 
                    gradient: 'from-green-500 to-teal-600',
                    category: 'Schemes'
                  },
                  { 
                    icon: TrendingUp, 
                    text: language === 'hi' ? 'जल जीवन मिशन की प्रगति दिखाएं' : 'Show me recent progress on Jal Jeevan Mission', 
                    gradient: 'from-purple-500 to-pink-600',
                    category: 'Development'
                  },
                  { 
                    icon: DollarSign, 
                    text: language === 'hi' ? 'वित्त मंत्री ने हाल ही में क्या कहा?' : 'What did the Finance Minister announce recently?', 
                    gradient: 'from-orange-500 to-red-600',
                    category: 'Finance'
                  },
                  { 
                    icon: Calendar, 
                    text: language === 'hi' ? 'इस सप्ताह की महत्वपूर्ण नीतियां' : 'What are the important policies announced this week?', 
                    gradient: 'from-cyan-500 to-blue-600',
                    category: 'Weekly'
                  },
                  { 
                    icon: Target, 
                    text: language === 'hi' ? 'सकारात्मक समाचार दिखाएं' : 'Show me positive news from last 7 days', 
                    gradient: 'from-teal-500 to-green-600',
                    category: 'Positive'
                  }
                ].map((item, idx) => {
                  const IconComponent = item.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(item.text)}
                      className="group relative text-left p-4 bg-gradient-to-br from-gray-50 to-white rounded-lg border border-gray-100 hover:border-transparent hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 overflow-hidden"
                    >
                      <div className={`absolute inset-0 bg-gradient-to-br ${item.gradient} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
                      <div className="relative">
                        <div className="flex items-start justify-between mb-3">
                          <div className={`w-9 h-9 bg-gradient-to-br ${item.gradient} rounded-lg flex items-center justify-center shadow group-hover:scale-110 transition-transform`}>
                            <IconComponent className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-xs font-semibold text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{item.category}</span>
                        </div>
                        <p className="text-xs font-medium text-gray-700 group-hover:text-gray-900 leading-relaxed">{item.text}</p>
                        <div className="flex items-center mt-2 text-xs text-gray-400 group-hover:text-gray-600">
                          <span>Click to ask</span>
                          <ChevronRight className="w-3 h-3 ml-1 group-hover:translate-x-1 transition-transform" />
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {messages.map(message => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl rounded-lg p-4 ${
              message.type === 'user' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-white border border-gray-200'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              
              {message.confidence !== undefined && (
                <div className="mt-2 text-xs opacity-75">
                  Confidence: {(message.confidence * 100).toFixed(0)}%
                </div>
              )}

              {message.sources && Array.isArray(message.sources) && message.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-200">
                  <p className="text-xs font-medium text-gray-700 mb-2 flex items-center">
                    <BookOpen className="w-3 h-3 mr-1" />
                    Sources ({message.sources.length}):
                  </p>
                  <div className="space-y-2">
                    {message.sources.slice(0, 3).map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-xs p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                      >
                        <div className="font-medium text-indigo-600 hover:underline">
                          {source.title || source.source}
                        </div>
                        {source.is_goi && (
                          <div className="text-gray-600 mt-1">
                            Government of India
                          </div>
                        )}
                        <div className="text-gray-500 mt-1">
                          {source.language} • {source.sentiment || 'neutral'}
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-2 text-xs opacity-60">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
            </div>
          </div>
        )}

          <div ref={messagesEndRef} />
        </div>



        {/* Input */}
        <div className="bg-white border-t border-gray-100 p-4 shadow-lg">
          <div className="max-w-6xl mx-auto">
            <form onSubmit={handleSubmit} className="relative">
              <div className="flex space-x-3">
                <div className="flex-1 relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={language === 'hi' ? 'अपना प्रश्न यहां टाइप करें...' : 'Ask anything about government news, policies, and schemes...'}
                    className="w-full pl-12 pr-4 py-3 text-base border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition-all shadow-sm hover:shadow bg-gray-50 focus:bg-white"
                    disabled={isLoading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !inputValue.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white rounded-xl hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center space-x-2 font-semibold text-base"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span>Ask Now</span>
                    </>
                  )}
                </button>
              </div>
            </form>
            
            {/* Enhanced Feature Badges */}
            <div className="mt-4 grid grid-cols-4 gap-3">
              {[
                { icon: Shield, text: 'Secure & Private', color: 'from-blue-500 to-cyan-500' },
                { icon: Zap, text: 'Lightning Fast', color: 'from-yellow-500 to-orange-500' },
                { icon: Brain, text: 'AI-Powered RAG', color: 'from-purple-500 to-pink-500' },
                { icon: Globe, text: '12 Languages', color: 'from-green-500 to-emerald-500' }
              ].map((badge, idx) => {
                const IconComponent = badge.icon;
                return (
                  <div key={idx} className="flex items-center justify-center space-x-2 text-xs text-gray-600 bg-gray-50 rounded-lg px-3 py-2 border border-gray-100">
                    <div className={`w-6 h-6 bg-gradient-to-br ${badge.color} rounded-lg flex items-center justify-center shadow-sm`}>
                      <IconComponent className="w-3 h-3 text-white" />
                    </div>
                    <span className="font-medium">{badge.text}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RAGAssistant;
