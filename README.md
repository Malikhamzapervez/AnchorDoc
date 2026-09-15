# AnchorDoc

A full-stack RAG application: a FastAPI backend for document indexing and Q&A, paired with a Next.js frontend that gives you a proper web interface — drag-and-drop uploads, real-time document status, and cited answers with clickable source references.

- Building a real frontend (Next.js + TypeScript + Tailwind) that talks to a FastAPI backend
- Asynchronous background indexing: upload returns instantly while indexing happens behind the scenes
- Smart chunking: tables are kept as atomic units so they aren't split mid-cell
- Markdown generation with page markers so citations always point to the right page

---

## Project Structure

```
lecture_18_document_butler/
├── backend/
│   ├── main.py              ← FastAPI app (port 8001)
│   ├── requirements.txt
│   ├── .env                 ← Your API keys (you create this)
│   ├── uploads/             ← Permanent file storage
│   ├── uploads_tmp/         ← Temp files during processing
│   ├── markdown_files/      ← Generated markdown with page markers
│   └── app/
│       ├── config.py        ← Settings from .env
│       ├── models.py        ← Pydantic models
│       ├── routes.py        ← URL routing
│       ├── api.py           ← Endpoint handlers
│       ├── file_loader.py   ← Multi-format file loading
│       ├── rag_service.py   ← Enhanced RAG pipeline
│       └── markdown_generator.py ← Smart chunking + page markers
│
└── frontend-next/
    ├── package.json         ← Node dependencies (Next.js, Tailwind, React)
    ├── next.config.ts       ← Next.js configuration
    └── app/                 ← Next.js App Router pages and components
```

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Backend runtime |
| Node.js 18+ | Frontend runtime (Next.js requires it) |
| Ollama | Local LLM for generating answers |
| Qdrant | Local persistent vector database, or optional Qdrant Cloud |

**Get Node.js:** https://nodejs.org (download the LTS version)  
**Get a free Qdrant Cloud cluster:** https://cloud.qdrant.io  
**Install Ollama:** https://ollama.com/download

---

## Backend Setup

### Step 1 — Open a terminal in the backend folder

```bash
cd AnchorDoc/backend
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Mac / Linux:
source venv/bin/activate
```

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Create your `.env` file

Create a file called `.env` inside `lecture_18_document_butler/backend/`:

```env
# Ollama (local, no API key required)
OLLAMA_BASE_URL=http://localhost:11434

# Optional Qdrant Cloud settings. Leave the placeholders unchanged to use
# the local persistent Qdrant database in backend/qdrant_storage/.
QDRANT_URL=qdrant url here
QDRANT_API_KEY=your qdrant api key here
QDRANT_PATH=qdrant_storage

# Optional
QDRANT_COLLECTION=document_butler
EMBEDDING_PROVIDER=huggingface
LLM_MODEL=llama3.2:3b
```

Before starting the backend, install Ollama and download the model:

```bash
ollama pull llama3.2:3b
```

### Step 5 — Start the backend server

```bash
python -m uvicorn main:app --reload --port 8001
```

You should see:
```
INFO     | Loading embedding model...
INFO     | Connecting to Qdrant...
INFO     | Connecting to Ollama LLM...
INFO     | Document Butler ready.
```

**Backend is now running at:** `http://localhost:8001`  
**API docs (Swagger UI):** `http://localhost:8001/docs`

---

## Frontend Setup

> Open a **second terminal** — keep the backend running in the first one.

### Step 1 — Open a terminal in the frontend folder

```bash
cd AnchorDoc/frontend-next
```

### Step 2 — Install Node dependencies

```bash
npm install
```

> This installs Next.js, React, Tailwind CSS, and other packages listed in `package.json`.  
> May take 1–2 minutes on first run.

### Step 3 — Start the development server

```bash
npm run dev
```

You should see:
```
▲ Next.js 16.x.x
- Local: http://localhost:3000
```

### Step 4 — Open the app

Go to **http://localhost:3000** in your browser.

---

## Using the App

### Upload documents
1. Drag and drop files onto the upload area, or click to browse
2. Supported formats: PDF, DOCX, TXT, MD, CSV
3. After uploading, each file shows a **Processing** status badge
4. When it turns **Ready**, the document is indexed and searchable

> The upload returns immediately — indexing runs in the background.  
> You can upload the next file while the previous one is still indexing.

### Ask a question
1. Type your question in the search box at the bottom
2. Click **Ask** or press Enter
3. The answer appears with **source citations** — each citation shows the file name and page number
4. Click a citation to jump to the exact passage

### Delete a document
- Click the trash icon next to any document in the document list
- All chunks for that document are removed from the vector database

---

## API Reference (Backend)

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/upload` | Upload files (returns immediately, indexes in background) |
| `POST` | `/query` | Ask a question, get answer + citations |
| `GET` | `/documents` | List all documents with their indexing status |
| `DELETE` | `/documents/{doc_id}` | Remove a document |
| `GET` | `/health` | Server status |

---

## Common Issues

**Backend won't start — Ollama connection error**
→ Make sure Ollama is running, `.env` is inside `backend/` (not the project root), and `ollama list` includes `llama3.2:3b`.

**Frontend shows "Failed to fetch"**
→ The backend is not running. Start it first with `python -m uvicorn main:app --reload --port 8001`.

**`npm install` fails**
→ Make sure Node.js 18+ is installed: `node --version`

**Port 3000 already in use**
→ Next.js will automatically try port 3001, 3002, etc. Check the terminal output for the actual URL.

**Documents stuck at "Processing"**
→ Check the backend terminal for error messages. Usually a Qdrant connection issue or missing API key.

**`sentence-transformers` is slow to load**
→ Normal on first run — the model downloads once and is cached locally.

---

## How It Works (Quick Overview)

```
Upload (async):
  File → background thread → file_loader.py
       → markdown_generator.py (adds <!-- page:N --> markers)
       → smart_chunk() (keeps tables atomic)
       → Embed chunks → Qdrant
       → Status: Processing → Ready

Query:
  Question → embed → Qdrant top_k search
           → LLM generates answer from context
           → Return answer + [{file_name, page_number, chunk_text, score}]
```

---

## Running Both Servers (Summary)

| Terminal | Command | URL |
|----------|---------|-----|
| Terminal 1 (Backend) | `cd backend && python -m uvicorn main:app --reload --port 8001` | http://localhost:8001/docs |
| Terminal 2 (Frontend) | `cd frontend-next && npm run dev` | http://localhost:3000 |

---

## Stopping Everything

- **Backend:** Press `Ctrl + C` in Terminal 1
- **Frontend:** Press `Ctrl + C` in Terminal 2
- **Deactivate venv:** `deactivate` in Terminal 1
