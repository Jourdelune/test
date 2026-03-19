# LangGraph Debug Test

Minimal setup to reproduce and debug edit/reload branching chat issues.

## Setup

### 1. Environment

Create a `.env` file in `backend/` with your OpenRouter API key:

```bash
OPENROUTER_API_KEY=sk-or-...
```

### 2. Install Backend Dependencies

```bash
cd backend
uv sync
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Running

### Backend (terminal 1)

```bash
cd backend
uv run langgraph dev
```

### Frontend (terminal 2)

```bash
cd frontend
npm run dev
```

## Usage

Open http://localhost:3000 in your browser.

- Type a message and press Enter
- Edit a user message with the pencil icon
- Regenerate an AI response with the refresh icon

Check the browser console for checkpoint logs when editing/regenerating.
