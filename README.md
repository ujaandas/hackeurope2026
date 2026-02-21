# GreenLinter - Green Code Optimizer

An AI-powered system that analyzes C++ code for energy-intensive patterns and automatically generates optimized, energy-efficient alternatives. Integrates into the Git workflow via a pre-commit hook, with a React dashboard for tracking sustainability metrics.

## Architecture

```
Developer commits C++ code
       |
       v
Pre-commit hook (Python)
       |
       v
FastAPI Backend (:8000)
  |-- Pattern Detection Engine (regex + brace-depth tracking)
  |   |-- O(n^2) nested loop / bubble sort detector
  |   |-- Excessive memory allocation detector
  |-- Energy Estimation (heuristic model)
  |-- AI Optimization (swappable providers)
  |   |-- Ollama/Llama (default, local, no API key needed)
  |   |-- Claude API (production option)
  |-- SQLite (optimization history)
       |
       v
React Dashboard (:3000)
  |-- KPI cards (kWh, CO2, EUR saved)
  |-- Before/after energy chart
  |-- Sustainability score gauge
  |-- Optimization history with code diff
  |-- ROI calculator
  |-- "Try It" manual analysis
```

## Quick Start

### With Docker Compose (Recommended)

```bash
docker compose up --build
```

This starts:
- **Backend API** at http://localhost:8000
- **Dashboard** at http://localhost:3000
- **Ollama** at http://localhost:11434

On first run, pull the CodeLlama model:
```bash
docker compose exec ollama ollama pull codellama
```

### Without Docker (Development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Ollama (separate terminal):**
```bash
ollama serve
ollama pull codellama
```

### Install Git Hook

```bash
chmod +x install-hook.sh
./install-hook.sh
```

Now when you commit C++ files, GreenLinter will automatically analyze and optimize them.

## How It Works

### Git Hook Workflow

1. Developer stages C++ files (`git add *.cpp`)
2. On `git commit`, the pre-commit hook fires
3. Hook sends staged file contents to the backend API
4. Backend detects energy anti-patterns (O(n^2) algorithms, memory allocation in loops, etc.)
5. If patterns found, AI generates optimized code
6. Optimized code overwrites the staged files and is re-staged
7. Commit proceeds with the optimized code

### Pattern Detection

Two energy anti-pattern detectors (regex-based with brace-depth tracking):

**1. Inefficient Sorting / O(n^2) Nested Loops**
- Detects nested for/while loops with swap patterns (bubble sort, selection sort)
- Detects generic O(n^2) nested iteration over collection sizes
- Suggests `std::sort()` (O(n log n) introsort)

**2. Excessive Memory Allocations**
- Detects `new`/`malloc`/`calloc` inside loop bodies
- Detects allocation/deallocation imbalance (memory leaks)
- Suggests pre-allocation, smart pointers (`std::unique_ptr`)

### Energy Estimation

Heuristic model (not real profiling) that estimates:
- **Energy score**: 0-100 (lower is better), based on pattern severity weights
- **kWh**: Annual energy consumption estimate (assumes 1000 runs/day)
- **CO2**: Using EU grid average of 0.385 kg CO2/kWh
- **Cost**: Using cloud compute rate of 0.25 EUR/kWh

### AI Optimization

Swappable providers with shared prompt design:
- **Ollama (default)**: Runs locally with CodeLlama, no API key needed
- **Claude**: Set `ANTHROPIC_API_KEY` and `AI_PROVIDER=claude` for production quality

The AI receives detected patterns with line numbers and generates complete optimized code with chain-of-thought reasoning.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | Analyze code for energy anti-patterns |
| POST | `/api/optimize` | Generate AI-optimized code |
| POST | `/api/hook` | Combined endpoint for git hook (analyze + optimize) |
| GET | `/api/dashboard` | Dashboard metrics and history |
| POST | `/api/roi` | ROI calculator |

### Example: Analyze Code

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "sort.cpp",
    "code": "void sort(int a[], int n) { for(int i=0;i<n;i++) for(int j=0;j<n;j++) if(a[i]>a[j]) { int t=a[i]; a[i]=a[j]; a[j]=t; } }",
    "language": "cpp"
  }'
```

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

21 tests covering pattern detection, energy estimation, and API endpoints.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `codellama` | Model to use for optimization |
| `ANTHROPIC_API_KEY` | (empty) | Claude API key (optional) |
| `AI_PROVIDER` | `ollama` | AI provider: `ollama` or `claude` |
| `DATABASE_PATH` | `./data/greenlinter.db` | SQLite database path |
| `GREENLINTER_API_URL` | `http://localhost:8000` | Backend URL (for git hook) |
| `GREENLINTER_ENABLED` | `true` | Enable/disable git hook |

## Architecture Decision Records

### ADR-1: Regex over AST for C++ Pattern Detection
**Decision**: Use regex with brace-depth tracking instead of full AST parsing (libclang/tree-sitter).
**Rationale**: Full C++ parsing adds significant complexity and setup time. For the two target anti-patterns (nested loops with swaps, allocation in loops), regex with brace-depth tracking is sufficient and can be implemented in under an hour. Trade-off: won't handle edge cases like braces in string literals, but works reliably for typical code.

### ADR-2: SQLite for Persistence
**Decision**: Use SQLite via aiosqlite instead of PostgreSQL.
**Rationale**: Zero infrastructure requirement. Single file, no additional container needed. Sufficient for MVP optimization history tracking. Can be upgraded to PostgreSQL later if needed.

### ADR-3: Ollama as Default AI Provider
**Decision**: Default to Ollama/CodeLlama instead of requiring a cloud API key.
**Rationale**: Works out of the box without credentials. Demo-friendly. Claude is available as a production upgrade path via the provider abstraction.

### ADR-4: Heuristic Energy Model
**Decision**: Use a heuristic scoring model instead of actual CPU/memory profiling.
**Rationale**: Real profiling requires executing code, which introduces security risks and complexity. The heuristic model provides internally consistent, directionally correct estimates (O(n^2) > O(n log n), alloc-in-loop > pre-alloc) that effectively demonstrate the concept.

### ADR-5: Auto-apply Hook with Exit 0
**Decision**: The pre-commit hook auto-applies optimizations and allows the commit to proceed.
**Rationale**: This matches the specified workflow where optimized code becomes the new diff. Users can review with `git diff --cached` before the commit message editor opens.

## Project Structure

```
greenlinter/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment-based settings
│   │   ├── models.py            # Pydantic models
│   │   ├── routers/             # API route handlers
│   │   ├── analyzer/            # Pattern detection engine
│   │   │   ├── engine.py        # Orchestrator
│   │   │   ├── patterns/        # Anti-pattern detectors
│   │   │   └── energy.py        # Energy estimation
│   │   ├── ai/                  # AI provider abstraction
│   │   └── db/                  # SQLite database layer
│   ├── tests/                   # Unit tests (21 tests)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/          # Dashboard components
│   │   └── api.js               # API client
│   ├── package.json
│   └── Dockerfile
├── hooks/
│   ├── pre-commit               # Shell wrapper
│   └── greenlinter_hook.py      # Hook logic
├── sample_code/                 # Demo C++ files with anti-patterns
├── docker-compose.yml
├── install-hook.sh
└── README.md
```
