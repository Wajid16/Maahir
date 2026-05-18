# Maahir Frontend Architecture

This document explains the core structure and design patterns used in the Maahir Flutter App.

## Overview
The mobile app is built with **Flutter** and uses the **Provider** package for state management. It features a premium Dark Mode design system with glassmorphism effects, complex animations, and Markdown rendering.

## Directory Structure
- `/lib/models` - Data structures mapping to backend API JSON (Provider, Booking, TraceStep).
- `/lib/screens` - Main UI pages (ChatScreen, Home, BookingDetail).
- `/lib/services` - Core business logic:
  - `api_service.dart`: Handles HTTP connections, health checks, and SSE Streaming logic.
  - `chat_provider.dart`: Global state manager for chat messages and session history.
- `/lib/theme` - Design system tokens (`AppColors`, gradients, typography).
- `/lib/widgets` - Reusable UI components (ProviderCard, ReasoningTrace, MarkdownBlock).

## SSE Streaming Engine
Because Challenge 2 requires visual representation of Agent reasoning, the app consumes Server-Sent Events (SSE) from the backend.
- `api_service.dart` uses `LineSplitter()` to safely reconstruct large JSON chunks from TCP boundaries.
- `chat_provider.dart` listens for event types (`agent_start`, `tool_call`, `text_chunk`, `done`) to progressively build the `ChatBubble` and the `ReasoningTraceWidget`.

## Visual Assets & Extensibility
- **Markdown:** AI responses are safely parsed using `markdown_widget` using a custom `MarkdownBlock` implementation to prevent rendering errors.
- **Maps API:** Provider locations are rendered securely using the Google Maps Static API directly inside `ProviderCard` images.
- **Sessions:** The app maintains a `sessionId`. Resetting the chat generates a new ID, enabling multi-session flows.
