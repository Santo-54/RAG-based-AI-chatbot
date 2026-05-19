import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for model embeddings/API calls
});

export const api = {
  /**
   * Get application health status and database connectivity info
   */
  getSystemStatus: async () => {
    const response = await client.get('/');
    return response.data;
  },

  /**
   * Send user message to the vector-based RAG chat pipeline
   * @param {string} query 
   */
  sendChatMessage: async (query) => {
    const response = await client.post('/chat', { query });
    return response.data;
  },

  /**
   * List all documents stored in the database
   */
  getDocuments: async () => {
    const response = await client.get('/documents');
    return response.data;
  },

  /**
   * Embed and upload a document to the vector database
   * @param {string} text 
   * @param {object} metadata 
   */
  uploadDocument: async (text, metadata = {}) => {
    const response = await client.post('/documents', { text, metadata });
    return response.data;
  },

  /**
   * Delete an existing document from vector store
   * @param {string} docId 
   */
  deleteDocument: async (docId) => {
    const response = await client.delete(`/documents/${docId}`);
    return response.data;
  }
};

export default api;
