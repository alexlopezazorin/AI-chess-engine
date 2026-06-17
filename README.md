# Chess Engine

A chess engine built with Next.js (frontend) and Python FastAPI (backend).

## Project Structure

```
chess-engine/
├── frontend/          # Next.js React application
├── backend/           # Python FastAPI backend
└── README.md
```

## Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Backend Setup

Navigate to the backend directory and set up a Python virtual environment:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt
python main.py
```

The backend API will be available at `http://localhost:8000`

## Features

- Interactive chess board UI
- Real-time move validation
- Game history tracking
- Checkmate and stalemate detection
- Pawn promotion
- Castling support
- En passant support
