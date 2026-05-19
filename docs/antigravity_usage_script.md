# Antigravity Usage Video Script (2-3 Minutes)

This video is specifically to show the judges *how* you used the Antigravity AI agent to build your application. Record your IDE (Cursor / Android Studio / VS Code) for this video.

## 1. Introduction (0:00 - 0:30)
*   **Visual:** Show your IDE with the Antigravity Chat panel open on the right side.
*   **Voiceover:** "For Challenge 2, our team extensively utilized the Google Antigravity Agent to accelerate our development. We used it not just as a code assistant, but as a lead architect."

## 2. Demonstrating the Workflow (0:30 - 1:30)
*   **Visual:** Open the `implementation_plan.md` artifact in the IDE.
*   **Voiceover:** "We used Antigravity's Planning Mode for every major feature. For example, when building the Antigravity Supervisor architecture, the AI researched our codebase and generated this exact Implementation Plan. Once we approved it, it autonomously refactored our Python backend."
*   **Visual:** Open the `task.md` or `walkthrough.md` artifact to show task tracking.

## 3. Highlighting specific AI interventions (1:30 - 2:30)
*   **Visual:** Show the `api_service.dart` or `backend/main.py` code where the SSE streaming logic is.
*   **Voiceover:** "When we encountered a critical bug where our large JSON trace payloads were breaking across network chunks, we delegated the debugging to Antigravity. It analyzed the byte stream, discovered the chunking issue, and autonomously rewrote our Dart API service to use a native `LineSplitter`."

## 4. Conclusion (2:30 - 3:00)
*   **Visual:** Show the terminal where Antigravity executed the git push or Cloud Run deployment.
*   **Voiceover:** "Antigravity even managed our deployments to Google Cloud Run and organized our GitHub repository. It was an indispensable tool for our team."
