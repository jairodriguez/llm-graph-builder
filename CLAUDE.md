# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The LLM Graph Builder is a full-stack application that transforms unstructured data (PDFs, DOCs, TXT, YouTube videos, web pages, etc.) into structured Knowledge Graphs stored in Neo4j using Large Language Models (LLMs) and the LangChain framework.

**Architecture:**
- **Backend**: FastAPI (Python) - main entry point is `backend/score.py`
- **Frontend**: React + TypeScript with Vite - uses Neo4j Needle UI components
- **Database**: Neo4j (version 5.23+) with APOC
- **Deployment**: Docker Compose for local, Google Cloud Run for production

## Development Commands

### Backend (FastAPI)

Located in `backend/` directory:

```bash
# Setup
cd backend
python -m venv envName
source envName/bin/activate  # On Windows: envName\Scripts\activate
pip install -r requirements.txt

# Development server
uvicorn score:app --reload

# API documentation
# Access at http://127.0.0.1:8000/docs (Swagger UI)
# or http://127.0.0.1:8000/redocs (ReDoc)
```

### Frontend (React + TypeScript)

Located in `frontend/` directory:

```bash
# Setup
cd frontend
yarn install

# Development server (runs on port 8080)
yarn run dev

# Build for production
yarn run build

# Linting
yarn lint

# Format code
yarn format

# Preview production build
yarn preview
```

### Full Stack (Docker Compose)

```bash
# Run entire application (frontend on :8080, backend on :8000)
docker-compose up

# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

### Testing

```bash
# Backend tests are in backend/ directory
cd backend
python test_commutiesqa.py  # Main test file
python Performance_test.py   # Performance tests
```

## Architecture & Code Structure

### Backend Architecture (`backend/src/`)

The backend follows a modular structure with clear separation of concerns:

**Core Processing Pipeline:**
1. `main.py` - Orchestrates the graph creation workflow for different source types (S3, GCS, local files, Wikipedia, YouTube, web pages)
2. `create_chunks.py` - Splits documents into chunks for processing
3. `llm.py` - Interfaces with various LLM providers to extract entities and relationships
4. `make_relationships.py` - Creates relationships between extracted entities
5. `post_processing.py` - Creates vector indexes, full-text indexes, and entity embeddings

**Data Access & Storage:**
- `graphDB_dataAccess.py` - All Neo4j database operations (31KB file, central to graph management)
- `document_sources/` - Adapters for different input sources:
  - `local_file.py` - Local file uploads
  - `s3_bucket.py` - AWS S3 integration
  - `gcs_bucket.py` - Google Cloud Storage
  - `youtube.py` - YouTube transcript processing
  - `wikipedia.py` - Wikipedia article extraction
  - `web_pages.py` - Web page scraping

**Chat/QA System:**
- `QA_integration.py` (26KB) - Implements multiple retrieval modes:
  - Vector search
  - Graph + Vector hybrid
  - Pure graph traversal
  - Fulltext search
  - Entity vector search
  - Global vector search
- Uses LangChain with Neo4jVector and GraphCypherQAChain

**Supporting Modules:**
- `communities.py` - Creates community detection in graphs
- `neighbours.py` - Graph traversal for related nodes
- `graph_query.py` - Query building and schema visualization
- `chunkid_entities.py` - Maps chunks to extracted entities
- `ragas_eval.py` - Evaluation framework integration
- `entities/source_node.py` - Data models for source documents
- `shared/constants.py` (33KB) - All Cypher queries and configuration constants
- `shared/common_fn.py` - Utility functions including embedding model loading
- `shared/schema_extraction.py` - Schema extraction from text

**LLM Support:**
The application supports multiple LLM providers configured via environment variables:
- OpenAI (GPT-3.5, GPT-4o, GPT-4o-mini)
- Google Gemini
- Diffbot
- Azure OpenAI
- Anthropic Claude
- Fireworks
- Groq
- Amazon Bedrock
- Ollama (for local models)
- Deepseek
- Other OpenAI-compatible APIs

### Frontend Architecture (`frontend/src/`)

**Key Files:**
- `App.tsx` - Main application component
- `Home.tsx` - Home page component
- `types.ts` (29KB) - All TypeScript type definitions for the application

**Component Organization:**
- `components/DataSources/` - File upload components for different sources (Local, AWS, GCS, Web)
- `components/ChatBot/` - Chat interface for querying the knowledge graph
- `components/Graph/` - Graph visualization components using Neo4j NVL
- `components/Layout/` - Layout components and navigation
- `components/UI/` - Reusable UI components (alerts, progress bars, icons, etc.)
- `components/Auth/` - Authentication components (Auth0 integration)
- `components/User/` - User management
- `components/Popups/` - Modal dialogs

**State Management:**
- `context/` - React contexts for global state
- `hooks/` - Custom React hooks

**Services & API:**
- `API/` - API client for backend communication
- `services/` - Business logic and service layer
- `utils/` - Utility functions including Queue implementation

### Configuration Files

**Backend Environment Variables** (see `backend/example.env`):
- Neo4j connection: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- LLM API keys: `OPENAI_API_KEY`, `DIFFBOT_API_KEY`, etc.
- Embedding configuration: `EMBEDDING_MODEL` (all-MiniLM-L6-v2, openai, or vertexai)
- Processing parameters: `MAX_TOKEN_CHUNK_SIZE`, `NUMBER_OF_CHUNKS_TO_COMBINE`
- Feature flags: `IS_EMBEDDING`, `ENTITY_EMBEDDING`, `GEMINI_ENABLED`, `GCS_FILE_CACHE`

**Frontend Environment Variables** (see `frontend/example.env`):
- Backend API: `VITE_BACKEND_API_URL` (default: http://localhost:8000)
- Supported sources: `VITE_REACT_APP_SOURCES` (local,youtube,wiki,s3,gcs,web)
- LLM models: `VITE_LLM_MODELS_PROD` for production models
- Chat modes: `VITE_CHAT_MODES` (vector,graph_vector,graph,fulltext,etc.)
- Chunk configuration: `VITE_CHUNK_SIZE`, `VITE_CHUNK_OVERLAP`, `VITE_TOKENS_PER_CHUNK`
- Authentication: `VITE_AUTH0_CLIENT_ID`, `VITE_AUTH0_DOMAIN`, `VITE_SKIP_AUTH`

## Important Patterns & Workflows

### Graph Creation Workflow

1. **Source Node Creation** - Files are registered as source nodes in Neo4j with metadata
2. **Document Loading** - Content is extracted from various sources via `document_sources/`
3. **Chunking** - Documents are split into processable chunks (`create_chunks.py`)
4. **LLM Processing** - Chunks are sent to LLMs to extract entities and relationships (`llm.py`)
5. **Graph Building** - Entities and relationships are created in Neo4j (`graphDB_dataAccess.py`)
6. **Post-Processing** - Indexes are created, embeddings generated, communities detected (`post_processing.py`)

### Retry Mechanism

The application has three retry options for failed processing (defined in `shared/constants.py`):
- `START_FROM_BEGINNING` - Reprocess entire document
- `START_FROM_LAST_PROCESSED_POSITION` - Continue from last successful chunk
- `DELETE_ENTITIES_AND_START_FROM_BEGINNING` - Clear existing entities and restart

### Chat Modes

Multiple retrieval strategies are available for Q&A:
- **Vector**: Pure vector similarity search
- **Graph+Vector**: Combines graph traversal with vector search
- **Graph**: Pure graph-based retrieval
- **Fulltext**: Full-text search
- **Entity Vector**: Vector search on entity embeddings
- **Global Vector**: Global context vector search

## Key Cypher Queries

The application uses extensive Cypher queries defined in `backend/src/shared/constants.py`:
- `QUERY_TO_GET_CHUNKS` - Retrieves document chunks for processing
- `QUERY_TO_DELETE_EXISTING_ENTITIES` - Clears entities for retry
- `QUERY_TO_GET_NODES_AND_RELATIONS_OF_A_DOCUMENT` - Gets graph for visualization
- Various queries for creating indexes, embeddings, and communities

## Neo4j Integration

- Main entry point is `score.py` which sets up FastAPI with Neo4j connection
- Uses `langchain-neo4j` for vector stores and graph QA chains
- Database driver is managed through `graph_query.py:get_graphDB_driver()`
- Requires Neo4j 5.23+ with APOC plugin installed
- Supports both Neo4j Aura DB and Aura DS

## LLM Model Configuration

For Ollama or custom models, use environment variables:
```bash
LLM_MODEL_CONFIG_ollama_<model_name>="model_name,http://host.docker.internal:11434"
```

The backend dynamically loads model configurations and routes to appropriate LLM providers via `llm.py`.

## Code Style

- **Backend**: Python with type hints where applicable, follows PEP 8
- **Frontend**: TypeScript with strict typing, uses ESLint and Prettier
- **Frontend formatting**: `yarn format` before commits (Husky pre-commit hook configured)
- **Frontend linting**: `yarn lint` to check for issues
