# CognitiveRAG — Premium AI Chatbot with Vector RAG & Mistral AI

A high-performance, production-ready, clean, and modular web application demonstrating vector-based **Retrieval-Augmented Generation (RAG)**.

This system runs vector embeddings locally using the standard `sentence-transformers` framework (avoiding expensive third-party embedding calls), stores dense vectors in MongoDB, retrieves them via an optimized Python cosine similarity engine, and builds conversational responses with the **Mistral AI API**.

---

## 🧠 System Architecture

```text
       User
        │
        ▼ (Renders Chat/Documents UI)
   [React App (Vite)]
        │
        ▼ (Axios REST Requests /chat & /documents)
  [FastAPI Backend]
        │
        ├─► [Local Embedding Service] ( sentence-transformers: all-MiniLM-L6-v2 )
        │
        ├─► [MongoDB Vector Store] ( Stores text + 384-dimensional dense vectors )
        │
        └─► [RAG Similarity Retrieval Engine] ( Python Cosine Similarity )
                │
                ▼ (Constructs final RAG context prompt)
         [Mistral LLM API]
                │
                ▼ (Generated Contextual Response)
             Response (to React UI)
```

---

## 📁 Project Structure

```text
project/
│
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint, Lifespan configuration, CORS & health router
│   │   ├── routes/
│   │   │   ├── chat.py         # /chat POST endpoint executing full RAG workflow
│   │   │   └── documents.py    # /documents CRUD routes for vector space additions/deletes
│   │   ├── services/
│   │   │   ├── embedding.py    # Local SentenceTransformer embedding service (Singleton)
│   │   │   ├── rag.py          # Similarity calculations and MongoDB retrieval service
│   │   │   └── mistral.py      # Mistral AI Chat Completions service with error handling
│   │   ├── models/
│   │   │   └── schemas.py      # Robust Pydantic request/response validation schemas
│   │   └── utils/
│   │
│   ├── .env                    # System configuration & keys (Git ignored)
│   ├── requirements.txt        # Backend dependencies
│   └── seed.py                 # Manual database seed script for CLI testing
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Dashboard framework & sidebar navigation
│   │   ├── App.css             # Glassmorphic visual stylings and animations
│   │   ├── api.js              # Axios backend connection client
│   │   ├── main.jsx            # React root mount script
│   │   └── components/
│   │       ├── Chat.jsx        # Conversational UI and source expandable details
│   │       └── DocManager.jsx  # Paste text files, list, search, and delete entries
│   ├── index.html              # Document layout (Google Fonts)
│   ├── package.json            # Vite React dependencies
│   └── vite.config.js          # Hot-reload compilation configurations
│
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisite
1. **Python 3.9+** installed locally.
2. **Node.js (v18+)** installed locally.
3. **MongoDB** instance running (can be a standard local database or a cloud Atlas connection).

---

### Step 1: Backend Setup

1. Open your terminal in the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create a Python Virtual Environment:
   ```bash
   python -m venv venv
   ```
3. Activate the environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
4. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure your environmental values in `backend/.env`:
   - Add your **Mistral API Key**.
   - Customize **MONGO_URI** if your instance is running on a cloud cluster or custom port.

---

### Step 2: Seed the Vector Space (Optional)

We supply a manual database seeding script. Running it will load 5 highly interesting, searchable documents into your MongoDB with their computed sentence-transformers vector embeddings. This allows testing the RAG chatbot out of the box without manual pasting!

From the activated backend environment, run:
```bash
python seed.py
```

---

### Step 3: Launch FastAPI Web Server

From the activated backend environment, launch Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
- Open your browser at [http://localhost:8000/docs](http://localhost:8000/docs) to view the interactive FastAPI Swagger Documentation.

---

### Step 4: Frontend Setup

1. Open a new terminal in the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install standard node modules:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
4. Open your browser at the displayed link (usually [http://localhost:5173](http://localhost:5173)) to enjoy the application!

---

## 🎨 Premium Visual Features

- **Obsidian Glassmorphism**: Tailored dark-mode dashboard styled with dynamic blur filters, floating purple glowing backgrounds, and modern cards.
- **RAG Trace Explorer**: Each assistant chat bubble has a retractable button to inspect exactly *which* database chunks were pulled, alongside computed mathematical similarity score percentages (e.g. `Similarity Score: 92.4%`).
- **Interactive Quick-Seed**: Includes a one-click database seeder inside the Knowledge collection page for effortless setup.
- **System Health Monitor**: Live-polling sidebar indicator tracking FastAPI status, local embedding load state, local/cloud MongoDB connection, and Mistral configurations.
