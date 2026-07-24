# AIVOA - AI-Powered Customer Complaint Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![Redux Toolkit](https://img.shields.io/badge/Redux%20Toolkit-1.9+-764ABC.svg?style=flat&logo=redux&logoColor=white)](https://redux-toolkit.js.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg?style=flat)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

An enterprise-grade **AI Copilot Web Application** designed for pharmaceutical **Quality Management System (QMS)** complaint intake. Powered by **LangGraph**, **FastAPI**, **PostgreSQL**, and **React + Redux Toolkit**, it automates the extraction, risk assessment, and formal documentation of customer complaints while keeping human quality agents in the loop.

### 🎥 Watch the Demo
[![AIVOA Demo Video](https://img.youtube.com/vi/HkvBCoAedxY/maxresdefault.jpg)](https://youtu.be/HkvBCoAedxY)

---

## 🌟 Key Features

* **🤖 LangGraph StateGraph Execution Pipeline**: Multi-node sequential agent workflow that extracts structured metadata, rewrites raw text into formal QMS descriptions, assesses root-cause risks, and determines severity (`Minor`, `Major`, `Critical`).
* **👥 Human-in-the-Loop Workflow**: Automatically populates form fields on the left pane while allowing quality engineers to review, edit, and verify all details before committing to the database.
* **📄 Document Intake (PDF / Text Upload)**: Upload raw PDF complaint documents or reports directly into the Copilot chat for automated text extraction via `pypdf`.
* **💬 Conversational Intent Detection**: Differentiates between general greetings (*"hi"*, *"hello"*) and actual complaint reports to prevent accidental form pollution.
* **🏛️ PostgreSQL QMS Ledger**: Persists verified complaint records in PostgreSQL with an in-app interactive QMS Ledger Modal and Swagger API support.
* **⚡ High-Availability Fallback Engine**: Seamless dual-layer processing with LLM extraction (Groq Llama 3.3 70B / OpenAI) supported by robust rule-based Regex fallbacks.

---

## 🏗️ System Architecture & Workflow

```
Customer Complaint (Text / PDF Upload)
        │
        ▼
   React + Redux UI (Split Screen)
        │
        ▼
   FastAPI Server (/api/v1/complaints/process)
        │
        ▼
 LangGraph StateGraph Workflow
        ├── Node 1: Extract Structured Data (Product, Batch, Dates, Customer, Category)
        ├── Node 2: Generate QMS Summary (Formal QMS Terminology Rewriting)
        ├── Node 3: Perform Risk Assessment (Severity & Root Cause Evaluation)
        └── Node 4: Recommend Next Action Step (Standard Operating Procedure SOP)
        │
        ▼
 Return Structured JSON Payload to Frontend
        │
        ▼
 React Form Auto-Populates (Left Pane) with Visual Highlights
        │
        ▼
 Quality Agent Reviews & Modifies Fields
        │
        ▼
 Commit to QMS Ledger (PostgreSQL Persistence)
```

---

## 📁 Directory Structure

```
AI-powered Customer Complaint Management System/
├── docker-compose.yml          # Docker container orchestration (PostgreSQL, FastAPI, Frontend)
├── README.md                   # Complete System Documentation
├── codebase_analysis.md        # Technical architecture report
├── backend/
│   ├── main.py                 # Backend runner entry point
│   ├── test_db.py              # PostgreSQL database connectivity test script
│   ├── create_db.py            # Automated database creator script
│   ├── requirements.txt        # Python backend dependencies
│   ├── .env                    # Environment configuration
│   ├── app/
│   │   ├── main.py             # FastAPI App configuration & CORS middleware
│   │   ├── core/
│   │   │   ├── config.py       # Centralized environment settings
│   │   │   └── database.py     # SQLAlchemy ORM Engine & Session Local setup
│   │   ├── models/
│   │   │   └── complaint.py    # SQLAlchemy Complaint Model (17 columns)
│   │   ├── schemas/
│   │   │   └── complaint.py    # Pydantic validation schemas
│   │   └── api/
│   │       └── routes/
│   │           └── complaints.py # REST Endpoints (/process, /upload, /commit, /)
│   └── langgraph_agent/
│       ├── state.py            # ComplaintState TypedDict definition
│       ├── nodes.py            # LangGraph Nodes (Extraction, Summary, Risk, Action)
│       └── workflow.py         # StateGraph orchestration & compilation
└── frontend/
    ├── package.json            # Node.js dependencies (React 18, Redux Toolkit, Lucide)
    ├── vite.config.js          # Vite build configuration
    └── src/
        ├── App.jsx             # Main Split-Screen Layout
        ├── main.jsx            # React root mount
        ├── index.css           # Modern Dark-Mode Glassmorphism Design Tokens
        ├── store/              # Redux Toolkit Slices (complaintSlice, chatSlice)
        └── components/         # UI Components
            ├── Header.jsx              # Navbar & Ledger Modal Trigger
            ├── ComplaintForm.jsx       # Left-Pane Human-in-the-Loop Form
            ├── AICopilotChat.jsx       # Right-Pane Interactive Chat & PDF Upload
            ├── QMSLedgerModal.jsx      # Modal showing PostgreSQL committed records
            └── NotificationToast.jsx   # In-app alert notifications
```

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18 | Declarative component UI |
| **State Management** | Redux Toolkit | Centralized state management & Async Thunks |
| **Styling** | Vanilla CSS3 | Modern dark-mode glassmorphism theme & CSS variables |
| **Icons** | Lucide React | Modern minimalist iconography |
| **Backend Framework** | FastAPI (Python 3.10+) | High-performance asynchronous REST API |
| **AI Workflow** | LangGraph | State graph workflow orchestration |
| **LLM Engine** | Groq Llama 3.3 70B / OpenAI | Natural Language entity extraction & risk reasoning |
| **ORM / DB** | SQLAlchemy + PostgreSQL | Relational database modeling & persistence |
| **PDF Extraction** | PyPDF | Page-by-page document text extraction |

---

## ⚙️ Database Schema (`complaints` Table)

When a complaint is committed, it is saved into PostgreSQL with the following schema:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` (PK) | Auto-incremented unique Complaint ID |
| `customer_name` | `VARCHAR(255)` | Reporting source (e.g. Hospital, Pharmacy) |
| `product_name` | `VARCHAR(255)` | Drug product name and strength |
| `batch_number` | `VARCHAR(255)` | Lot/Batch identification number |
| `manufacturing_date` | `VARCHAR(100)` | Batch manufacture date |
| `expiry_date` | `VARCHAR(100)` | Batch expiration date |
| `facility` | `VARCHAR(255)` | Manufacturing plant location |
| `impacted_material` | `VARCHAR(255)` | Dosage form / packaging material affected |
| `complaint_category` | `VARCHAR(255)` | Standard defect category |
| `raw_complaint_text` | `TEXT` | Original submitted report |
| `qms_summary` | `TEXT` | AI-rewritten formal QMS summary |
| `suggested_severity` | `VARCHAR(50)` | Risk rating (`Minor`, `Major`, `Critical`) |
| `risk_assessment` | `TEXT` | Detailed engineering root-cause assessment |
| `recommended_action` | `TEXT` | Recommended SOP action step |
| `status` | `VARCHAR(50)` | Complaint status (Default: `Logged to QMS Ledger`) |
| `created_at` | `TIMESTAMP` | Record creation timestamp |
| `updated_at` | `TIMESTAMP` | Record update timestamp |

---

## ⚡ Quick Start & Installation

### Option A: Manual Local Setup (Recommended for Development)

#### 1. Backend Setup (FastAPI + LangGraph)
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database (if not already created)
python create_db.py

# Start FastAPI server
python main.py
```
* Backend API will run at: `http://localhost:8000`
* Interactive Swagger Docs: `http://localhost:8000/docs`

#### 2. Frontend Setup (React + Vite)
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
* Frontend UI will run at: `http://localhost:5173`

---

### Option B: Docker Compose Setup

```bash
docker-compose up --build
```
* Frontend UI: `http://localhost:5173`
* Backend API Docs: `http://localhost:8000/docs`

---

## 🧪 Testing Sample Complaints

Try pasting any of these test cases into the **AI Copilot Chat**:

#### Case 1: Packaging Defect (Major)
```text
Metro Health Hospital reported broken aluminum foil seals and crushed tablets in Ibuprofen Tablets 400mg. Batch IB-9082. Manufacturing date January 2026. Expiry December 2027.
```

#### Case 2: Contamination / Toxicity Risk (Critical)
```text
St. Jude Regional Clinic submitted an urgent report regarding foreign black metallic particles observed inside Metformin Suspension 500mg. Batch MET-4029. Manufacturing date February 2026. Expiry January 2028.
```

#### Case 3: Label Typo (Minor)
```text
CarePlus Pharmacy reported a typographical error on the outer carton dosage instructions of Paracetamol Tablets 650mg. Batch PCT-1104. Manufacturing date March 2026. Expiry October 2027.
```

---

## 🔗 API Documentation Links

* **Swagger Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **OpenAPI Specification**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
