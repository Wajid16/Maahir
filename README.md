# Maahir - Google AI Hackathon 2026

![Maahir Logo](App%20Screenshots/logo.png)

Maahir (ماہر) is an intelligent, multi-agent platform connecting the informal economy of Pakistan with a structured, reliable service network. Powered by the **Google Gen AI SDK (Vertex AI)** and built on **Flutter**, Maahir uses a dynamic Agentic Orchestrator to natively understand intent, discover the best service providers, and seamlessly book appointments.

## 🏆 Challenge 2 Submission
This repository contains the complete source code for our Challenge 2 submission, showcasing advanced agentic workflows and multi-modal integration.

## 📂 Project Structure
*   **`backend/`**: Python FastAPI backend featuring the **Antigravity Supervisor Architecture**.
*   **`flutter_app/`**: Production-ready Flutter mobile application featuring real-time Agent Reasoning Traces (SSE Streaming) and a custom Dark Mode design system.
*   **`docs/`**: Comprehensive team documentation.
    *   [Backend Architecture](docs/BACKEND_ARCHITECTURE.md)
    *   [Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)
    *   [API Contract](docs/API_CONTRACT.md)
    *   [Contributing Guide](docs/CONTRIBUTING.md)

## 🧠 The Antigravity Supervisor Pattern
Instead of a rigid pipeline, Maahir uses an advanced **Supervisor Agent** to route tasks dynamically based on user intent:
1.  **Planner (Intent Parser)**: Classifies requests (Urdu, English, Roman Urdu).
2.  **Discovery Match Agent**: Scores providers using a 10-factor weighted algorithm (distance, rating, skill match, etc.).
3.  **Booking Simulation Agent**: Handles dynamic pricing and conflict resolution.
4.  **Follow-up Agent**: Manages disputes and post-service workflows.

*Feature Highlight: Auto-Rerouting Resilience - If a provider rejects a booking (simulated), the Supervisor automatically loops back to the Discovery agent to find the next best provider without throwing an error!*

## 🚀 Getting Started
Please see the [Contributing Guide](docs/CONTRIBUTING.md) for step-by-step instructions on setting up your `.env` files, initializing the Python backend, and running the Flutter app.

---
*Built with ❤️ by Team Wajid for Google AI Seekho Hackathon 2026*
