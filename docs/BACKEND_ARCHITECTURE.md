# Maahir Backend Architecture

This document explains the core structure and design patterns used in the Maahir Orchestrator backend.

## Overview
The backend is built with **FastAPI** and uses the **Google Gen AI SDK (ADK)** for agentic orchestration. The architecture revolves around a **Supervisor Pattern**, replacing a rigid sequential pipeline with dynamic reasoning.

## Directory Structure
- `/agents` - Contains the agent definitions (Supervisor, Planner, Discovery, Booking, Followup).
- `/tools` - Python modules containing external tools (Firestore, Maps, Pricing, Notification, Scheduling).
- `main.py` - The FastAPI entry point containing routes (`/api/chat`, `/api/chat_stream`).
- `config.py` - Centralized configuration for API keys, GCP settings, and scoring weights.

## The Antigravity Supervisor Pattern
Instead of running agents in a strict sequence (e.g., A -> B -> C), the system uses a **Supervisor Agent** that dynamically routes user intents.

### The Pipeline Flow:
1. **Input:** User sends a natural language request (English, Urdu, Roman Urdu).
2. **Planner (Intent Parser):** Analyzes the text and determines the exact `service_type`, `location`, and decides which sub-agent is needed. It sets a `route`.
3. **Dynamic Routing:** The Supervisor checks the `route`.
    - If `discovery_match`, it runs the **Discovery Agent** to search and score providers based on 10-factor weights.
    - If `booking_simulation`, it runs the **Booking Agent** to handle dynamic pricing, scheduling, and DB persistence.
    - If `followup`, it handles disputes or reminders.
    - If `direct_response`, it skips tools and replies directly (e.g., greetings).

### Auto-Rerouting (Resilience)
If a provider rejects a booking (simulated 20% rejection rate), the Supervisor automatically detects the failure and loops *back* to the Discovery agent to find the next best provider without throwing an error to the user!

## Server-Sent Events (SSE) Streaming
The `/api/chat_stream` endpoint uses SSE to stream real-time updates to the mobile app.
- It intercepts `tool_call` and `agent_complete` events from the ADK to build a live **Reasoning Trace**.
- It suppresses raw JSON LLM thoughts from bleeding into the user's chat text.
- It formats a beautiful final response upon completion.

## Deployment
The backend is Dockerized and deployed via Google Cloud Run (`deploy.ps1`). It uses Vertex AI authentication (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) when hosted.
