import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, BookOpen, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import api from '../api';

export default function Chat({ onNavigateToDocs, isDbConnected }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeSourcesIndex, setActiveSourcesIndex] = useState({});
  const messagesEndRef = useRef(null);

  // Standard preset prompts
  const suggestions = [
    { question: "What is Mistral AI?", desc: "Learn about the AI company" },
    { question: "What is FastAPI?", desc: "Discover the web framework" },
    { question: "How does local vector search work?", desc: "Learn how similarity search computes" },
    { question: "Explain RAG architecture.", desc: "Understand Retrieval Augmented Generation" }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || input.trim();
    if (!text) return;

    if (!textToSend) setInput('');

    // Append user message
    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Execute standard RAG pipeline
      const data = await api.sendChatMessage(text);
      
      // Append assistant message with retrieved sources
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        context: data.context || []
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      const errorMessage = {
        role: 'assistant',
        content: `❌ Error: ${err.response?.data?.detail || 'Failed to connect to the backend server. Please verify your FastAPI app is running.'}`,
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSources = (index) => {
    setActiveSourcesIndex(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-history">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-logo">🧠</div>
            <h1 className="welcome-title">CognitiveRAG Assistant</h1>
            <p className="welcome-subtitle">
              Ask questions naturally. The system will retrieve relevant context from your MongoDB vector collection and use Mistral AI to construct accurate, clean answers.
            </p>
            
            <div className="suggestion-grid">
              {suggestions.map((item, idx) => (
                <div 
                  key={idx} 
                  className="suggestion-chip" 
                  onClick={() => handleSendMessage(item.question)}
                >
                  <div className="suggestion-question">{item.question}</div>
                  <div className="suggestion-action">{item.desc} →</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>
              <div className="message-content-wrapper">
                <div className="message-text">
                  {msg.content}
                </div>

                {/* Display Vector RAG Sources if present */}
                {msg.role === 'assistant' && msg.context && msg.context.length > 0 && (
                  <div className="sources-card">
                    <button className="sources-toggle" onClick={() => toggleSources(idx)}>
                      <BookOpen size={14} />
                      <span>
                        {activeSourcesIndex[idx] ? 'Hide sources' : `Show retrieved vector sources (${msg.context.length})`}
                      </span>
                      {activeSourcesIndex[idx] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                    
                    {activeSourcesIndex[idx] && (
                      <div className="sources-list">
                        {msg.context.map((source, sIdx) => (
                          <div key={sIdx} className="source-item">
                            <div className="source-meta">
                              <span className="source-category">
                                Category: {source.metadata?.category || 'General'}
                              </span>
                              <span className="source-score">
                                Match Score: {(source.score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="source-body">
                              "{source.text}"
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Skeleton loading bubble */}
        {isLoading && (
          <div className="message-bubble assistant">
            <div className="avatar">AI</div>
            <div className="message-content-wrapper">
              <div className="message-text">
                <div className="skeleton-container">
                  <div className="skeleton-line medium"></div>
                  <div className="skeleton-line"></div>
                  <div className="skeleton-line short"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input container */}
      <div className="chat-input-wrapper">
        <input
          type="text"
          className="chat-input"
          placeholder={isDbConnected ? "Ask the assistant about your uploaded documentation..." : "Warning: Backend/MongoDB not connected."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          disabled={isLoading}
        />
        <button 
          className="chat-submit-btn" 
          onClick={() => handleSendMessage()}
          disabled={isLoading || !input.trim()}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
