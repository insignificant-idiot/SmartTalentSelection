# Smart Talent Selection Engine

A full‑stack AI system that ranks resumes against job descriptions using vector search (ChromaDB) and a local LLM (Qwen3‑4B via Docker Model Runner).

## Quick Start (Windows + Docker Model Runner)

This is the **recommended** way to run the project on Windows.

### 1. Install Prerequisites

- **Docker Desktop for Windows** (v4.30 or later) with WSL 2 backend  
  [Download](https://www.docker.com/products/docker-desktop/)
- **Git for Windows** (optional, but convenient)  
- **WSL 2** with an Ubuntu distribution (installed automatically by Docker Desktop)

### 2. Clone the Repository

```bash
git clone https://github.com/your-org/smart-talent-engine.git
cd smart-talent-engine
```

**Performance tip:** Keep the code inside the WSL filesystem (`\\wsl$\Ubuntu\home\...`) – never on `C:\` – for native I/O speed.

### 3. Start the Local LLM with Docker Model Runner

Open a **WSL terminal** or **PowerShell** and run:

```bash
docker model run hf.co/Qwen/Qwen3-4B-GGUF:Q4_K_M
```

This command:
- Downloads the 4‑bit quantised Qwen3‑4B model (~2.5 GB) from Hugging Face.
- Starts an inference server at `http://localhost:12434`.
- Keep this terminal open – the model stays resident.

> **First run only** – subsequent starts are instant.

### 4. Configure the Backend

Create a file `.env` in the project root:

```env
DATABASE_URL=sqlite:///./talent.db
CHROMA_PATH=./chroma_db
LOCAL_LLM_URL=http://localhost:12434
LOCAL_LLM_MODEL=hf.co/Qwen/Qwen3-4B-GGUF:Q4_K_M
```

### 5. Install Tesseract OCR (Required for image resumes)

**Windows:**
- Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- During setup, tick **“Add Tesseract to PATH”**
- Install the English language pack

Verify with:
```cmd
tesseract --version
```

### 6. Run Backend (Native)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# or `source venv/bin/activate` on WSL

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Run Frontend (Native)

Open a **new terminal** (do not close the model or backend).

```bash
cd frontend
npm install
npm run dev
```

### 8. Access the Application

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Running Everything in Docker (Alternative)

If you prefer to containerise the backend and frontend as well, use this `docker-compose.yml`:

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./talent.db
      - CHROMA_PATH=/chroma_db
      - LOCAL_LLM_URL=http://host.docker.internal:12434   # ← reach the model
      - LOCAL_LLM_MODEL=hf.co/Qwen/Qwen3-4B-GGUF:Q4_K_M
    volumes:
      - ./app:/app
      - ./uploads:/uploads
      - ./chroma_db:/chroma_db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host
```

Then:

```bash
docker-compose up --build
```
