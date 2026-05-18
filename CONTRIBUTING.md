# Contributing to Maahir

Welcome to the Maahir team! This guide will help you get the project running locally and outline our contribution standards.

## Project Setup

### 1. Backend (Python/FastAPI)
1. Ensure you have Python 3.10+ installed.
2. Navigate to the `backend/` directory.
3. Create a virtual environment: `python -m venv venv` and activate it.
4. Install requirements: `pip install -r requirements.txt`.
5. Run the server: `python main.py` or use `uvicorn main:app --reload`.
6. **Environment Variables:** You MUST configure your `.env` file with `GOOGLE_API_KEY` or `GEMINI_API_KEY`. If deploying, ensure `GOOGLE_GENAI_USE_VERTEXAI` is properly set.

### 2. Frontend (Flutter)
1. Ensure you have the latest Flutter SDK installed.
2. Navigate to the `flutter_app/` directory.
3. Run `flutter pub get` to download dependencies.
4. Set your backend URL in `lib/services/api_service.dart` (`_baseUrl`). When running on an Android emulator, use `http://10.0.2.2:8000`. For physical devices, use the deployed Cloud Run URL.
5. Run the app: `flutter run`.

## Best Practices
- **Flutter UI:** Always strictly adhere to the `AppColors` palette in `app_theme.dart`. Do not use default Flutter Blue!
- **Backend Prompts:** When modifying agent prompts (in `agents/`), ensure instructions are explicit. The models respond best when you define precise JSON schemas and context constraints (e.g., Pakistan-only).
- **Tool Creation:** All new backend capabilities must be registered as Python tools in `tools/` and injected into the appropriate agent's `tools` array.

## Known Issues & Backlog
- **Gradle Timeout:** If you see network timeouts compiling the APK (`repo.maven.apache.org`), this is an ISP block. Switch to a mobile hotspot or disable firewalls.
- **Offline Fallback:** If the backend is down, the frontend automatically falls back to an offline mock response in `chat_provider.dart`. Ensure you disable this when doing live testing.
