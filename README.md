# Maahir ماہر - AI Service Orchestrator for Pakistan's Informal Economy

![Maahir Banner](flutter_app/assets/logo_premium.png) <!-- Update with actual banner path if available -->

> **Google AI Hackathon 2026 - Challenge 2 Submission**  
> *Empowering the informal economy (plumbers, electricians, tutors, beauticians) through Agentic AI.*

---

## 🚀 The Problem & Solution
The informal economy operates largely through fragmented WhatsApp messages and phone calls, resulting in inefficient matching, missed opportunities, and a poor user experience. 

**Maahir** solves this by acting as an **Intelligent Service Orchestrator**. Using a multi-agent backend powered by **Google Antigravity**, it understands complex, multi-lingual natural language requests (Urdu, Roman Urdu, English), intelligently matches users with the best local providers, and simulates the entire booking and follow-up process autonomously.

---

## ✨ Key Features
1. **Intelligent Intent Parsing:** Speak or type in Roman Urdu ("Mujhe kal subah G-13 mein AC technician chahiye"). The system extracts service type, location, and urgency.
2. **Dynamic Provider Matching:** Real-time semantic matching with our mock database of 35+ verified local providers.
3. **Agentic Reasoning UI:** Watch the AI "think". The UI features a real-time expandable reasoning trace showing exactly how the agents parse, match, and book.
4. **Voice Input:** Built-in Speech-to-Text for accessibility.
5. **WhatsApp Integration:** Instantly share confirmed booking receipts to WhatsApp.

---

## 🧠 Architecture: Powered by Google Antigravity

Maahir's backend breaks away from rigid rule-based logic and employs a **Supervisor-Worker Agentic Architecture** built with Google Antigravity. 

### The Agentic Pipeline:
1. **`intent_parser` Agent:** Analyzes the raw user prompt. Uses tool calls to extract `service_category`, `location_sector`, `time_preference`, and `urgency`.
2. **`provider_discovery` Agent:** Queries the Firestore database based on the extracted intent to find available providers in the specified sector.
3. **`matcher` Agent:** Evaluates providers based on distance, rating, and historical performance, assigning a dynamic "Match Score".
4. **`booking` Agent:** Simulates the creation of a calendar slot and generates pricing estimates.
5. **`followup` Agent:** Schedules an automated SMS/WhatsApp reminder for post-service feedback.

**Server-Sent Events (SSE):** The Flutter frontend connects to the Antigravity backend via SSE. As each agent begins work, makes a tool call, or completes a task, the backend streams these state changes, which the Flutter app dynamically renders as a "Reasoning Trace" inside the chat bubble.

---

## 🛠️ Technologies & Tools
* **Backend:** Google Antigravity ADK, FastAPI, Python 3.12
* **Frontend:** Flutter (Dart), Material 3 Design
* **Database:** Simulated Google Cloud Firestore (Mock JSON for prototype)
* **Real-time Comms:** Server-Sent Events (SSE)
* **Native Integrations:** `speech_to_text` (Voice), `url_launcher` (Maps), `share_plus` (WhatsApp)

---

## ⚙️ Setup & Installation

### Prerequisites
* Flutter SDK (`^3.7.0`)
* Android Studio / Xcode

### Running the App Locally
1. Clone the repository.
2. Navigate to the flutter app directory:
   ```bash
   cd flutter_app
   ```
3. Install dependencies:
   ```bash
   flutter pub get
   ```
4. Run the app:
   ```bash
   flutter run
   ```
   *Note: Ensure you test on a physical device to utilize the Microphone (Speech-to-Text) and WhatsApp Share features.*

### Backend (Mock Mode)
For the purpose of this hackathon submission, the Flutter app is configured to use an advanced **Mock Streaming Engine**. This engine perfectly simulates the asynchronous multi-agent pipeline, delays, and text streaming without requiring the live Python backend to be active, ensuring a flawless demo experience.

---

## ⚠️ Assumptions & Limitations
1. **Database:** The provider directory is currently a static JSON mock representing sectors in Islamabad (G-13, F-8, etc.). In a production environment, this would be a live geospatial query in Firestore or PostGIS.
2. **Payments:** Payment gateways (Easypaisa/JazzCash) are not integrated. The system assumes Cash on Delivery (COD) for the prototype.
3. **Speech-to-Text:** The voice input feature relies on the device's native OS speech recognition capabilities. Accuracy in pure Urdu depends on the device's locale settings.
4. **Booking:** "Booking" is simulated. A real implementation would require a dedicated provider-facing app to accept/reject requests.

---
*Built with ❤️ for Pakistan's informal sector.*
