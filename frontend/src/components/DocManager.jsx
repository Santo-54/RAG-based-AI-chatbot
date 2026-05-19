import React, { useState, useEffect } from 'react';
import { Database, Plus, Trash2, FileText, Sparkles, RefreshCw } from 'lucide-react';
import api from '../api';

export default function DocManager({ onRefreshStatus }) {
  const [documents, setDocuments] = useState([]);
  const [text, setText] = useState('');
  const [category, setCategory] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedingProgress, setSeedingProgress] = useState('');

  // Default seed documents that can be injected from React
  const sampleDocs = [
    {
      text: "Mistral AI is a prominent French artificial intelligence company founded in April 2023 by former researchers from Meta and Google DeepMind. It is renowned for creating highly efficient, open-weight language models such as Mistral 7B, Mixtral 8x7B, and commercial systems like Mistral Large.",
      category: "AI Company"
    },
    {
      text: "FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints. Built on top of Starlette and Pydantic, FastAPI is extremely fast, reduces code duplication, and automatically generates interactive Swagger UI documentation.",
      category: "Web Framework"
    },
    {
      text: "The sentence-transformers Python library provides state-of-the-art methods for generating dense vector embeddings for sentences, paragraphs, and images. The pre-trained model 'all-MiniLM-L6-v2' embeds text into a 384-dimensional space, making it highly optimized for local semantic search and clustering.",
      category: "Machine Learning"
    },
    {
      text: "MongoDB is a leading document-oriented, NoSQL database designed for high scalability and flexibility. It stores data in BSON documents. Standard MongoDB is widely used to store text elements along with dense vectors, allowing custom applications to perform extremely rapid cosine similarity searches.",
      category: "Database"
    },
    {
      text: "Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses by retrieving relevant documents from an external custom database (e.g. vector search) based on the user's query, appending this context to the prompt, and feeding it to the LLM to prevent hallucinations.",
      category: "AI Architecture"
    }
  ];

  const fetchDocuments = async () => {
    setIsLoadingDocs(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleAddDocument = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setIsSubmitting(true);
    try {
      const metadata = { category: category.trim() || 'General' };
      await api.uploadDocument(text.trim(), metadata);
      setText('');
      setCategory('');
      await fetchDocuments();
      if (onRefreshStatus) onRefreshStatus();
    } catch (err) {
      alert(`Failed to add document: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!confirm("Are you sure you want to delete this document from the vector space?")) return;

    try {
      await api.deleteDocument(docId);
      await fetchDocuments();
      if (onRefreshStatus) onRefreshStatus();
    } catch (err) {
      alert("Failed to delete document.");
    }
  };

  const handleSeedDatabase = async () => {
    setIsSeeding(true);
    try {
      for (let i = 0; i < sampleDocs.length; i++) {
        const doc = sampleDocs[i];
        setSeedingProgress(`Embedding doc ${i + 1}/${sampleDocs.length}: ${doc.category}...`);
        await api.uploadDocument(doc.text, { category: doc.category, source: 'auto_seed' });
      }
      setSeedingProgress('Database seeded successfully!');
      setTimeout(() => setSeedingProgress(''), 3000);
      await fetchDocuments();
      if (onRefreshStatus) onRefreshStatus();
    } catch (err) {
      alert("Seeding failed: " + err.message);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="doc-manager-grid">
      {/* Upload/Add Form */}
      <div className="doc-panel">
        <h2 className="panel-title">
          <Plus size={20} className="text-primary" />
          <span>Ingest New Document</span>
        </h2>
        
        <form onSubmit={handleAddDocument}>
          <div className="form-group">
            <label className="form-label">Document content</label>
            <textarea
              className="form-textarea"
              placeholder="Paste raw text, documentation, article paragraphs, or FAQs here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
              disabled={isSubmitting || isSeeding}
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Category / Label</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Web Dev, Machine Learning, FAQ..."
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={isSubmitting || isSeeding}
            />
          </div>
          
          <button 
            type="submit" 
            className="submit-btn" 
            disabled={isSubmitting || isSeeding || !text.trim()}
          >
            {isSubmitting ? (
              <>
                <RefreshCw size={18} className="animate-spin" />
                <span>Generating Embedding...</span>
              </>
            ) : (
              <>
                <Database size={18} />
                <span>Embed & Store Document</span>
              </>
            )}
          </button>
        </form>

        {/* Dynamic Seeding Option */}
        <div className="seed-alert-box">
          <div>
            <strong>💡 Quick Seed Option</strong>
            <p style={{ marginTop: '4px', opacity: 0.8 }}>
              Don't have custom text ready? Pre-populate your database with high-quality documents about Mistral AI, FastAPI, MongoDB, RAG, and Vector embeddings!
            </p>
          </div>
          <button 
            className="seed-btn-inline" 
            onClick={handleSeedDatabase}
            disabled={isSeeding || isSubmitting}
          >
            {isSeeding ? 'Seeding...' : 'Seed Sample Knowledge'}
          </button>
          {seedingProgress && <div style={{ fontSize: '11px', color: '#67e8f9' }}>{seedingProgress}</div>}
        </div>
      </div>

      {/* List Panel */}
      <div className="doc-panel">
        <div className="panel-title" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={20} className="text-secondary" />
            <span>Knowledge Base Collection ({documents.length})</span>
          </div>
          <button 
            onClick={fetchDocuments} 
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            title="Refresh List"
          >
            <RefreshCw size={16} className={isLoadingDocs ? 'animate-spin' : ''} />
          </button>
        </div>

        <div className="doc-list">
          {isLoadingDocs && documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              Loading documents...
            </div>
          ) : documents.length === 0 ? (
            <div className="doc-list-empty">
              <Database size={32} />
              <div>
                <strong>No documents stored yet</strong>
                <p style={{ fontSize: '12px', marginTop: '4px', opacity: 0.7 }}>
                  Vector space is empty. Add documents using the form on the left or click "Seed Sample Knowledge" to get started!
                </p>
              </div>
            </div>
          ) : (
            documents.map((doc) => (
              <div key={doc.id} className="doc-card">
                <div className="doc-card-header">
                  <span className="doc-card-badge">
                    {doc.metadata?.category || 'General'}
                  </span>
                  <button 
                    className="doc-delete-btn" 
                    onClick={() => handleDeleteDocument(doc.id)}
                    title="Remove Document"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="doc-card-body">
                  "{doc.text}"
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
