"""
Maahir — Agent Pipeline v3.0 (Antigravity Supervisor)
Exports root_agent: The dynamic Supervisor that routes to specialized sub-agents.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.supervisor import supervisor_agent

# ── Root Agent: Antigravity Supervisor ──────────────────────────────────────
# The supervisor parses intents and dynamically routes the request to:
# 1. discovery_match_agent (Search & Ranking)
# 2. booking_simulation_agent (Pricing, Schedule, Action)
# 3. followup_agent (Reminders, Disputes)

root_agent = supervisor_agent
