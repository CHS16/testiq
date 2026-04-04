# IntentIQ Ecosystem

IntentIQ is an intelligent, full-stack AI-powered communication ecosystem. It consists of an autonomous voice screening agent, a scalable FastAPI backend, and a modern React-based SaaS dashboard. IntentIQ allows businesses to automatically field incoming calls, understand the caller's intent, and make split-second routing decisions while providing comprehensive real-time analytics.

## Project Structure

This repository is split into three main components:

- [`frontend/`](./frontend): The React + Vite application for navigating interactive insights and call metrics.
- [`backend/`](./backend): The FastAPI application providing REST endpoints backed by MongoDB.
- [`Intent_IQ/livekit-voice-agent/`](./Intent_IQ/livekit-voice-agent): `Nebula`, the LiveKit-powered AI Voice Assistant.

---

## 1. LiveKit Voice Agent (`Nebula`)

**Location:** `Intent_IQ/livekit-voice-agent`

Nebula is an AI-powered call-screening assistant designed to answer incoming calls, understand the caller's intent, and autonomously decide whether to transfer the call to a human or end it. 

### Key Features:
- **Autonomous Call Handling:** Uses LiveKit Agents API to handle real-time VoIP/SIP audio streams.
- **Multimodal AI Integration:** Relies on Deepgram for Speech-to-Text, ElevenLabs for Text-to-Speech, and Google Gemini 2.5 Flash as the conversational LLM.
- **Intelligent Screening:** Analyzes conversation context and uses Groq (Llama-3-70b) to extract intents, urgency scores, and summaries.
- **Automated Data Feed:** Directly formats call data and pushes interaction metrics into the shared MongoDB database (`intent_iq_db`).

*For more details, see the [Voice Agent README](./Intent_IQ/livekit-voice-agent/README.md).*

---

## 2. Backend API Server

**Location:** `backend/`

A high-performance FastAPI server constructed with asynchronous database operations using `motor`. This component serves as the bridge between the stored interactions (persisted by the voice agent) and the frontend dashboard display.

### Key Features:
- **FastAPI & Uvicorn:** Lightning-fast routing and server ASGI performance.
- **MongoDB Integration:** Full CRUD capabilities interacting with the `intent_iq_db` database via asynchronous Mongo connections.
- **Pydantic Validation:** Ensures data schema consistency via robust models.
- **Filtering Options:** Includes parameter-based filtering for granular interaction querying.

*For more details, see the [Backend README](./backend/README.md).*

---

## 3. Frontend Dashboard

**Location:** `frontend/`

The frontend application provides a responsive, professional-grade interface for managing AI-driven analytics, viewing real-time call logs, and monitoring overall interaction health.

### Key Features:
- **React 18 & Vite:** Lightning-fast module buffering and robust front-page performance.
- **Tailwind CSS:** Modern, highly-customizable UI aesthetics.
- **Real-Time Log Ingestion:** Interfaces directly with the backend API (`axios`) to automatically map new interactions seamlessly onto the dashboard.
- **Component Styling & Routing:** Clean navigation paths utilizing `React Router DOM` and custom SVG icon support by `Lucide React`.

*For more details, see the [Frontend README](./frontend/README.md).*

---

## Getting Started

To run the complete IntentIQ stack locally:

### 1. Database
Make sure you have a local MongoDB instance running (port 27017 by default) so both the backend and the AI Agent can seamlessly access `intent_iq_db`.

### 2. Backend server
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*(The backend API will run on `http://localhost:8000`)*

### 3. Frontend server
```bash
cd frontend
npm install
npm run dev
```
*(The frontend dashboard will run on `http://localhost:5173`)*

### 4. Voice Agent
```bash
cd Intent_IQ/livekit-voice-agent
pip install -e .  # Ensure .env.local is configured with all required API keys
python Nebula.py dev
```
*(You will use the LiveKit CLI or cloud dashboard to manage incoming streams to the agent)*

---

*This overarching structure allows clear tracking of intent analysis starting from an initial audio SIP call, through LLM diagnostics, and directly into an insightful frontend GUI overview.*
