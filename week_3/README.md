## Project Overview

This project is a containerized AI Resume Helper ChatBot consisting of:
- a frontend service responsible for user interaction
- a backend service handling API requests via FastAPI, and LLM for processing user input

.. designed to run via Docker for local development and deployment.

---

## System Architecture

The application is split into independent services:

* **Frontend (Web UI)**

  * Sends user messages and files to backend API
  * Renders chat history and responses

* **Backend (API Server)**

  * Exposes `/chat` endpoint
  * Processes user input and optional PDF text
  * Communicates with AI model layer

* **AI Model Service (or integration)**

  * Generates responses based on prompts + context

All services communicate over a shared Docker network.

---

## Setup Instructions

### Prerequisites

Ensure the following are installed:

* Docker
* Docker Compose
* Python
* uv

---

## Testing

### Frontend Testing

Test cases:

* Send plain text message → expect response displayed
* Upload PDF → verify text extraction and inclusion in request
* Invalid input → ensure UI handles errors gracefully

Manual testing:

* Open browser dev tools
* Inspect network requests to `/chat`
* Verify payload correctness

---

## Limitations

* Chat history is not persisted across sessions
* PDF processing may fail for scanned or image-based documents
* AI responses depend on model limitations (hallucination possible)
* No rate limiting or request throttling
* No streaming responses (if not implemented)

---
