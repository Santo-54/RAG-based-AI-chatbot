import React, { useState, useEffect } from 'react';
import { MessageSquare, Database, Cpu, HelpCircle, RefreshCw } from 'lucide-react';
import Chat from './components/Chat';
import DocManager from './components/DocManager';
import api from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [systemStatus, setSystemStatus] = useState({
    database: { connected: false },
    mistral_llm: { configured: false }
  });
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);

  const checkStatus = async () => {
    setIsCheckingStatus(true);
    try {
      const data = await api.getSystemStatus();
      setSystemStatus(data.services);
    } catch (err) {
      console.error("Backend status check failed:", err);
      setSystemStatus({
        database: { connected: false, error: 'Cannot reach backend server' },
        mistral_llm: { configured: false }
      });
    } finally {
      setIsCheckingStatus(false);
    }
  };

  useEffect(() => {
    checkStatus();
    // Periodically verify connectivity status
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Sidebar Panel */}
      <aside className="sidebar">
        <div className="brand-section">
          <div className="brand-icon">
            <Cpu size={22} />
          </div>
          <span className="brand-title">CognitiveRAG</span>
        </div>

        <nav className="nav-links">
          <button 
            className={`nav-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={18} />
            <span>Chat Assistant</span>
          </button>
          
          <button 
            className={`nav-button ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            <Database size={18} />
            <span>Knowledge Base</span>
          </button>
        </nav>

        {/* Real-time Status Card */}
        <div className="status-card">
          <div className="status-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Services Status</span>
            <button 
              onClick={checkStatus} 
              style={{ background: 'transparent', border: 'none', color: 'var(--text-dark)', cursor: 'pointer' }}
              disabled={isCheckingStatus}
            >
              <RefreshCw size={12} className={isCheckingStatus ? 'animate-spin' : ''} />
            </button>
          </div>
          
          <div className="status-item">
            <span className="status-label">Embeddings Model:</span>
            <span className="status-badge" style={{ color: 'var(--secondary)' }}>
              all-MiniLM
            </span>
          </div>

          <div className="status-item">
            <span className="status-label">MongoDB Connect:</span>
            <span className="status-badge">
              <span className={`badge-dot ${systemStatus.database?.connected ? 'dot-green' : 'dot-red'}`} />
              {systemStatus.database?.connected ? 'Online' : 'Offline'}
            </span>
          </div>

          <div className="status-item">
            <span className="status-label">Mistral AI API:</span>
            <span className="status-badge">
              <span className={`badge-dot ${systemStatus.mistral_llm?.configured ? 'dot-green' : 'dot-orange'}`} />
              {systemStatus.mistral_llm?.configured ? 'Configured' : 'Missing Key'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main View Area */}
      <main className="content-area">
        <header className="top-bar">
          <h2 className="page-title">
            {activeTab === 'chat' ? 'Conversational AI Assistant' : 'Knowledge Collection Manager'}
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
            <HelpCircle size={16} />
            <span>Mistral-Powered Vector RAG</span>
          </div>
        </header>

        <section className="main-view">
          {activeTab === 'chat' ? (
            <Chat 
              onNavigateToDocs={() => setActiveTab('documents')} 
              isDbConnected={systemStatus.database?.connected}
            />
          ) : (
            <DocManager onRefreshStatus={checkStatus} />
          )}
        </section>
      </main>
    </div>
  );
}
