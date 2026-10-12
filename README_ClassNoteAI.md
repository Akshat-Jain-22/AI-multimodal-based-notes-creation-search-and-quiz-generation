# ClassNote AI — Multimodal Lecture Notes, Search & Quiz Generation

ClassNote AI is a classroom-focused learning platform that turns lecture recordings and learning materials into structured notes, searchable knowledge, and practice quizzes. Teachers can organize content into classes and share it with enrolled students, while students can revisit lecture notes, ask questions grounded in course materials, and practice with generated quizzes.

**Suggested GitHub repository name:** `classnote-ai`

## Features

- **Multimodal lecture ingestion:** Process lecture audio/video and PowerPoint/PDF materials through the available pipeline stages.
- **Speech-to-text transcription:** Transcribe lecture audio with Faster-Whisper.
- **Screen and slide extraction:** Extract visible slide content with OCR and parse PowerPoint content.
- **Transcript refinement and translation:** Correct transcripts and translate content/notes into supported languages.
- **AI-generated notes:** Combine extracted lecture content into structured notes and polish the output.
- **Semantic search and grounded Q&A:** Retrieve relevant passages from indexed lecture content and answer questions using the LLM pipeline.
- **Quiz generation:** Create practice questions from course materials, including diagram support where available.
- **Classroom workflows:** Teachers create classes and share join codes; students join classes and access the content for those classes.
- **Role-based access:** Teacher and student roles control access to class management and lecture upload features.
- **Lecture library:** Browse lectures, view notes, and access extracted media.
- **Language preferences:** Save a preferred language for notes, search answers, and quizzes.
- **Web application:** React interface connected to a FastAPI backend.
- **Vector search:** ChromaDB with sentence-transformer embeddings supports semantic retrieval.

## Tech Stack

### Frontend
- React 18
- Vite
- React Router
- React Markdown
- KaTeX / remark-math / rehype-katex for mathematical notation

### Backend and storage
- Python
- FastAPI
- SQLite for users, sessions, classes, enrollments, and lecture metadata
- HTTP-only session cookies
- Pydantic

### AI / ML pipeline
- Faster-Whisper for audio transcription
- Groq API and LangChain for LLM-based correction, note generation, question answering, and quiz generation
- Hugging Face Sentence Transformers for embeddings
- ChromaDB for vector storage and retrieval
- OpenCV, Pillow, and Tesseract OCR for image/screen processing
- python-pptx and pdf2image for document/slide extraction
- Matplotlib for generated diagrams and charts

## Architecture

```text
Lecture audio / video / PDF / PPTX
                |
                v
     Transcription + OCR + extraction
                |
                v
    Transcript correction / translation
                |
                v
       Content fusion and chunking
                |
                v
        AI notes generation + polish
                |
                v
       Search chunks + ChromaDB index
                |
        +-------+--------+
        |                |
        v                v
   Grounded Q&A      Quiz generation
        |                |
        +-------+--------+
                |
                v
      React UI served via Vite
                |
                v
          FastAPI backend
                |
                v
       SQLite classroom metadata
```

## Repository Structure

```text
classnote-ai/
├── backend/
│   ├── api.py                 # FastAPI app and API endpoints
│   ├── auth.py                # Registration, login, logout, session auth
│   ├── db.py                  # SQLite schema and persistence
│   └── pipeline_worker.py     # Background pipeline worker
├── frontend/
│   ├── src/
│   │   ├── components/        # Shared UI components and route protection
│   │   ├── context/           # Authentication state
│   │   ├── pages/             # Auth, classes, upload, notes, search, quiz
│   │   └── api.js             # API client
│   └── package.json
├── scripts/
│   ├── run_pipeline.py        # End-to-end lecture processing pipeline
│   ├── audio_to_text.py       # Audio transcription
│   ├── screen_to_text.py      # Screen OCR / extraction
│   ├── pptx_to_text.py        # PowerPoint extraction
│   ├── generate_notes.py      # Notes generation
│   ├── build_search_index.py  # ChromaDB indexing
│   ├── search_notes.py        # Retrieval and grounded Q&A
│   └── generate_quiz.py       # Quiz generation
├── requirements.txt           # AI pipeline and shared Python dependencies
└── requirements_backend.txt   # Lightweight backend dependency list
```

## Getting Started

### Prerequisites

- Python version compatible with the pinned dependencies (Python 3.11/3.12 is a reasonable starting point; check package compatibility for your platform).
- Node.js and npm.
- A Groq API key for LLM-powered stages.
- Tesseract OCR installed and available on your system PATH if OCR is required.
- Poppler utilities installed and available on your PATH if PDF-to-image conversion is required.
- Sufficient disk space for speech-recognition models, embedding models, uploaded media, and vector indexes.

### 1. Clone the repository

```bash
git clone https://github.com/Akshat-Jain-22/AI-multimodal-based-notes-creation-search-and-quiz-generation.git
cd AI-multimodal-based-notes-creation-search-and-quiz-generation
```

If you rename the repository, update the clone URL to match the new name.

### 2. Configure environment variables

Create `scripts/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Keep API keys private. Never commit `.env` files or real credentials.

The frontend uses `VITE_API_BASE_URL`. The repository includes `frontend/.env.example`; copy it to `frontend/.env` and adjust the URL if necessary:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Install Python dependencies

Create and activate a virtual environment from the repository root.

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install a CPU-compatible PyTorch build first, following the official PyTorch installation selector for your platform. Then install the project dependencies:

```bash
pip install -r requirements.txt
```

For an API-only environment, `requirements_backend.txt` lists the lightweight FastAPI server dependencies. The complete application still imports pipeline modules, so AI dependencies must also be installed before using lecture processing, search, or quiz features.

### 4. Run the backend

From the repository root:

```bash
cd backend
python -m uvicorn api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

### 5. Run the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints in the terminal, typically `http://localhost:5173`.

Make sure `frontend/.env` has `VITE_API_BASE_URL=http://localhost:8000`. Restart the Vite server after changing environment variables.

## Typical Workflow

1. Register as a **teacher** and sign in.
2. Create a class for a subject or section.
3. Share the class join code with students.
4. Upload a lecture recording and, where supported, accompanying PDF or PowerPoint material.
5. Wait for the background processing job to finish.
6. Open the lecture notes and review the generated content.
7. Use class-scoped semantic search to ask questions about lecture material.
8. Generate practice quizzes from the class's indexed lectures.
9. Students register as **students**, join a class with its code, and access that class's available lectures, notes, search, and quizzes.

Exact upload fields and supported combinations are defined by the API and UI; consult the interactive API documentation if your request differs from the UI workflow.

## API Overview

The FastAPI application exposes routes for authentication, classroom management, lecture processing, notes/media access, search, and quiz generation.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Create a teacher or student account |
| `POST` | `/auth/login` | Sign in and establish a session cookie |
| `POST` | `/auth/logout` | End the current session |
| `GET` | `/auth/me` | Get the current user's profile |
| `PATCH` | `/auth/language` | Update preferred language |
| `POST` | `/classes` | Create a class (teacher) |
| `POST` | `/classes/join` | Join a class using a code (student) |
| `GET` | `/classes` | List accessible classes |
| `GET` | `/classes/{class_id}/lectures` | List class lectures |
| `POST` | `/lectures/process` | Start lecture processing |
| `GET` | `/lectures/jobs/{job_id}` | Check a processing job |
| `GET` | `/lectures/{lecture_id}/notes` | Retrieve lecture notes |
| `POST` | `/search` | Search course content / answer a question |
| `POST` | `/quiz` | Generate a quiz from course content |
| `DELETE` | `/lectures/{lecture_id}` | Delete a lecture |

For full request schemas, response formats, and all available endpoints, open `/docs` while the backend is running.

## Running the Processing Pipeline Directly

The pipeline modules can also be used independently for debugging or evaluation. For the end-to-end command-line options, run:

```bash
python scripts/run_pipeline.py --help
```

The pipeline can include audio transcription, transcript correction and translation, screen OCR, PowerPoint extraction, content fusion, chunking, note generation, polishing, and search-index construction. The exact stages depend on the supplied inputs and command-line options.

## Data, Storage, and Generated Artifacts

- SQLite classroom and account metadata is stored under `backend/`.
- Pipeline scripts create working directories and generated artifacts under `scripts/`.
- ChromaDB indexes are persisted locally; they may need to be rebuilt if source content or embedding configuration changes.
- Audio/video processing and model downloads can consume substantial disk space.
- Avoid committing private lecture recordings, student information, API keys, generated caches, local databases, or other sensitive data.

Before publishing, inspect the repository and `.gitignore` to ensure that sample recordings, databases, pipeline outputs, model caches, and credentials are not accidentally included.

## Limitations

- AI-generated notes, answers, translations, and quizzes can contain errors. Review important information against the original lecture.
- Search quality depends on extraction, chunking, embeddings, index contents, and retrieval thresholds.
- Processing speed and resource usage depend on recording length, model size, hardware, and API limits.
- The background job state is stored in a local JSON file; it is suitable for a small/local deployment but is not a durable distributed job queue.
- The current CORS configuration is permissive for local development. Restrict allowed origins and configure secure cookies and HTTPS before production deployment.
- API-based generation depends on the configured provider, account limits, and network access.

## Future Improvements

- Add a durable background queue and job persistence.
- Add automated end-to-end tests for upload, processing, search, and quiz workflows.
- Add pipeline-stage evaluation reports with reproducible datasets and metrics.
- Improve upload limits, file validation, retention controls, and production security settings.
- Add deployment configuration and observability for production use.

## Contributing

Bug reports, ideas, and pull requests are welcome. For larger changes, open an issue first to discuss the proposal.

## License

No license is specified in this repository. Add a `LICENSE` file before granting others permission to reuse, modify, or redistribute the code.
