# 🏗️ Implementation Guide – University AI Assistant

Welcome, teammate!  
This is your “deep dive” guide to the code and infra powering our university’s AI assistant. You’ll find **step-by-step** explanations, dev tips, and even a few jokes for morale. Bookmark this—future you will thank you! 🚀

---

## 💡 How the System Actually Works (Step by Step)

### 1. User → Frontend

- User opens their browser and goes to our assistant’s webpage (on the intranet, e.g. `http://ai.uni.local`).
- The UI is a React single-page app. Users:
    - Type a question.
    - (Optionally) upload PDFs (onboarding, HR, policies, research—whatever we let them!).
    - See the chat update in real-time as answers come back.

### 2. Frontend → Backend (API)

- User actions trigger AJAX calls to the backend (FastAPI).
    - Example:
        - `POST /api/chat` — user message (and optional file IDs)
        - `POST /api/upload` — PDF upload
- The frontend never talks to OpenWebUI or any model directly—it always goes through our backend.

### 3. Backend → OpenWebUI (API)

- Our backend securely holds the OpenWebUI API token and makes requests on behalf of the user.
- **For chat:**
    - Backend takes the user question, bundles it with any relevant document/file IDs.
    - Calls OpenWebUI’s `/api/chat/completions` endpoint.
    - OpenWebUI does RAG (retrieval-augmented generation):
        - Semantic search over ingested PDFs (vector DB)
        - Gathers the most relevant text snippets
        - Forms a prompt for the local LLM (Ollama)
- **For document upload:**
    - Backend receives file, calls OpenWebUI’s `/api/v1/files/` endpoint.
    - OpenWebUI does OCR via Apache Tika, chunks and indexes document.

### 4. OpenWebUI → Ollama / Tika

- **Ollama**: Runs the actual LLM, e.g., LLaMA-2. The AI “thinks” here.
- **Tika**: OCRs any PDFs (especially scanned/image-based ones).
- **Chroma DB**: OpenWebUI stores embeddings of text chunks for fast retrieval.

### 5. Everything Returns

- OpenWebUI sends the AI’s answer (and sometimes additional info) back up the chain:
    - → backend → frontend → user’s browser.

---

## 🗂️ Project Structure In-Depth

### `/backend`

#### `main.py`
- Entrypoint for FastAPI backend.
- Sets up routes, loads config, initializes logging.
- If running as `python main.py`, spins up the API server.

#### `requirements.txt`
- All Python package dependencies (e.g. FastAPI, requests, python-dotenv, tqdm for ingestion, etc.)

#### `config.py`
- Loads environment variables (like API endpoints, tokens) into Python variables.
- This is the only place you should hard-code secrets/paths.

#### `api/routes.py`
- Defines all API endpoints (`/api/chat`, `/api/upload`, etc.)
- Handles:
    - Parsing incoming requests.
    - Validating user input (Pydantic schemas if you want to be fancy).
    - Calls the appropriate service (e.g. chat_service, document_service).

#### `api/openwebui_client.py`
- Contains functions to talk to OpenWebUI.
    - E.g. `def send_chat_completion(...)`, `def upload_file(...)`.
- Handles API key authentication, error checking, and serialization.

#### `services/chat_service.py`
- Main business logic for chat:
    - Builds messages, handles context.
    - Calls `openwebui_client.send_chat_completion(...)`
    - (You could add post-processing here—like redacting sensitive info.)

#### `services/document_service.py`
- Handles document upload workflow:
    - Accepts file from API, reads content.
    - Calls `openwebui_client.upload_file(...)`.
    - Returns OpenWebUI’s file ID and upload status.

#### `utils/logger.py`
- Basic logging wrapper (can swap in fancier logging later).
- Use `logger.info("message")`, `logger.error("oops!")` everywhere.

#### `scripts/initial_ingest.py`
- **One-off or batch job** for bulk-uploading our 10,000+ PDFs.
- Walks a directory tree, uploads each PDF to OpenWebUI.
- Logs progress, skips files already uploaded (can check by file name or hash).
- *Run this ONCE per file set!*

---

### `/frontend`

#### `public/index.html`
- The root HTML template (includes `<div id="root"></div>`).

#### `src/App.tsx`
- Main React component—renders the whole UI.
- Houses state/context, manages navigation.

#### `src/index.tsx`
- Entrypoint for React app. Renders `<App />` into the DOM.

#### `src/components/ChatWindow.tsx`
- Manages all chat logic (state for messages, handles user input, calls API).
- Renders messages using `MessageBubble`, upload area, and input form.

#### `src/components/MessageBubble.tsx`
- Styles and displays individual chat messages (AI vs user).
- Handles markdown rendering (use `react-markdown`).

#### `src/components/UploadArea.tsx`
- Handles drag-and-drop or button-based PDF uploads.
- Shows progress indicators and error messages.

#### `src/components/Navbar.tsx`
- The top navigation bar (branding, model selector, etc).

#### `src/services/api.ts`
- Centralizes all frontend→backend API calls.
    - `sendMessage()`, `uploadFile()`, etc.
- Handles fetch/AJAX logic, error handling, etc.

#### `package.json`, `tsconfig.json`
- Usual suspects: JS/TS dependencies, build config.

---

### `/docs`

#### `architecture.png`
- (See README) Diagram of entire architecture. If not present, generate using [diagrams.net](https://diagrams.net) or draw.io and save here!

#### `README.md`
- You’re reading the sample version right now.

#### `IMPLEMENTATION_GUIDE.md`
- This file. Put tips, “gotchas,” and internal notes here for future devs.

---

### `/docker-compose.yml`
- Launches everything with one command: backend, frontend, OpenWebUI, Ollama, and Tika.
- Mounts volumes for persistent storage.
- Configures internal Docker networking (so `openwebui`, `ollama`, `tika`, and `backend` containers can talk to each other by service name).

---

### `/.env.example`
- Template of all required environment variables. Copy to `.env` and fill in the real secrets.

---

## 🏃‍♂️ Step-by-Step: Deploying and Using

### 1. Environment Setup

- Make sure you have Docker and Docker Compose installed.
- Clone the repo.
- Copy `.env.example` to `.env` and set:
    ```env
    OPENWEBUI_URL=http://openwebui:3000
    OPENWEBUI_API_KEY=<fill-in>
    TIKA_URL=http://tika:9998
    # (others as needed)
    ```
- Download/prep your AI model with Ollama (see OpenWebUI’s [docs](https://github.com/open-webui/open-webui)):
    ```bash
    ollama pull llama2:13b
    ```
    (or whatever model you need)

### 2. Bulk Ingest PDFs (ONE-TIME)

- Place all your PDFs in a local directory.
- Run:
    ```bash
    python backend/scripts/initial_ingest.py
    ```
    - This will upload all docs via API, trigger OCR & embedding in OpenWebUI.
    - Script logs progress and skips already-uploaded files.
    - *Pro tip:* Run with `nohup` or `tmux` for huge PDF sets—don’t let SSH time out! 😅

### 3. Launch the System

```bash
docker-compose up -d
```

- All containers start, networked together.
- First launch will take longer (images download, models load).

### 4. Access the UI

- Open your browser and go to:  
  [http://localhost:5000](http://localhost:5000) (or your mapped frontend port)
- You should see the chat UI. Test chat and upload functionality!

---

## 🔧 Development & Troubleshooting

### Backend

- Develop in `/backend`.
- Hot-reload with:
    ```bash
    uvicorn main:app --reload --port 5000
    ```
- Test endpoints with curl or Postman.

### Frontend

- Develop in `/frontend`.
- Hot-reload with:
    ```bash
    npm install
    npm start
    ```
- Runs on port 3000 by default (proxy API calls to backend).

### Logs

- Use `docker-compose logs <service>` to check logs.
- Backend logs go to console and file (via `logger.py`).
- Check OpenWebUI logs if API calls fail.

---

## ⚠️ Common Gotchas

- **API key errors:** 401s mean your token is wrong or expired.
- **CORS issues:** In dev, set CORS in backend to allow `localhost:3000` origin.
- **Slow answers:** Try a smaller model in Ollama, or get a beefier server. AI models love RAM!
- **PDF upload failures:** Check Tika logs—some PDFs are stubborn, try re-saving them with a different PDF engine.

---

## 🤓 Advanced: Adding Features

### Add a new LLM

- Pull model with Ollama.
- Update OpenWebUI config to recognize it.
- (Optional) Add a model selector in frontend `Navbar.tsx`.

### Add support for more file types

- Tika handles `.pdf`, `.docx`, etc. By default, only `.pdf` is uploaded.
- To accept other formats, extend `UploadArea.tsx` and backend validation logic.

### Improve multi-user experience

- For per-user chat history or document privacy, integrate SSO or session tokens.
- OpenWebUI supports RBAC if you want to give different access levels.

### Add logging/monitoring

- Integrate Prometheus/Grafana for metrics if you want full “ops” visibility.
- For now, stick to logs and alerts!

---

## 📬 Questions? Stuck?

- Ask your fellow team members.
- Leave questions as TODOs in code for review.
- If all else fails: take a walk, grab coffee, and try again!

---

## 👩‍🔬 Final Thoughts

This project is for us, by us. Improve it, document your changes, and make the next dev’s life easier.  
Keep this guide updated as we evolve the project!

Happy coding (and may your AI always return the right answer on the first try 🤞)!
