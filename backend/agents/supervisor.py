"""
Maahir — Agent: Antigravity Supervisor
Core orchestrator that parses intent (multi-lingual) and dynamically routes to sub-agents.
Demonstrates Plan -> Decision -> Action -> Follow-up.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import AsyncGenerator
from google.adk.agents import Agent, LlmAgent
from config import GEMINI_MODEL

from agents.discovery_match_agent import discovery_match_agent
from agents.booking_simulation_agent import booking_simulation_agent
from agents.followup_agent import followup_agent

SUPERVISOR_INSTRUCTION = """You are the Maahir (ماہر) Antigravity Supervisor Agent.

Your job is to understand the user's intent (in English, Urdu, or Roman Urdu),
extract key details, and decide which sub-agent should handle the next step.

## Input
User message: {user_message}
Session state: {state}

## Context & Constraints (CRITICAL)
- You are operating EXCLUSIVELY in Pakistan (specifically Islamabad and Rawalpindi).
- Assume all prices are in PKR.
- Assume all locations (G-13, F-8, Blue Area, Bahria Town, etc.) are in Islamabad/Rawalpindi.
- Use Pakistan Standard Time (PKT).
- If a user asks for a service without specifying a city, default to Islamabad.
- DO NOT ask clarifying questions about currency or country.

## Your Task
1. Analyze the user's message.
2. Extract `service_type` (e.g., ac_technician, plumber), `location` (e.g., G-13), and `requested_time`.
3. If the user is just greeting, set `route` to "direct_response" and provide a helpful reply in `direct_reply`.
4. If the user wants to find or book a service, set `route` to "discovery_match".
5. If the user is agreeing to book the provider from the previous turn, set `route` to "booking_simulation".
6. If the user is asking for a follow-up or complaining about a past booking, set `route` to "followup".
7. If information is missing (like location), set `route` to "direct_response" and ask for it.

## Output Format
Return ONLY valid JSON:
{{
  "parsed_intent": {{
    "service_type": "ac_technician",
    "location": "G-13",
    "requested_time": "Tomorrow morning",
    "category": "service_request",
    "language_detected": "Roman Urdu"
  }},
  "route": "discovery_match",
  "direct_reply": "Apki service request process ho rahi hai...",
  "reasoning": "User requested an AC technician in G-13. Routing to discovery_match to find providers."
}}
"""

_planner_agent = LlmAgent(
    name="planner",
    model=GEMINI_MODEL,
    instruction=SUPERVISOR_INSTRUCTION,
    output_key="supervisor_plan"
)

class AntigravitySupervisorAgent(Agent):
    def __init__(self, name="maahir_supervisor"):
        super().__init__(name=name)
        self._worker_agents = {
            "discovery_match": discovery_match_agent,
            "booking_simulation": booking_simulation_agent,
            "followup": followup_agent
        }

    async def _run_impl(self, ctx) -> AsyncGenerator[any, None]:
        # 1. Run the planner to get intent and route
        plan_stream = _planner_agent.run(ctx)
        if hasattr(plan_stream, '__aenter__'):
            async with plan_stream as stream:
                async for event in stream:
                    event.author = "planner"
                    yield event
        else:
            async for event in plan_stream:
                event.author = "planner"
                yield event
                
        # 2. Extract decision
        raw_plan = ctx.session.state.get("supervisor_plan", "{}")
        try:
            plan = json.loads(raw_plan)
        except:
            plan = {"route": "direct_response", "direct_reply": "I'm sorry, I couldn't understand that."}
            
        ctx.session.state["parsed_intent"] = json.dumps(plan.get("parsed_intent", {}))
        route = plan.get("route", "direct_response")
        
        # 3. Dynamic Routing
        max_retries = 2
        for attempt in range(max_retries):
            if route in self._worker_agents:
                target_agent = self._worker_agents[route]
                target_stream = target_agent.run(ctx)
                if hasattr(target_stream, '__aenter__'):
                    async with target_stream as stream:
                        async for event in stream:
                            event.author = route
                            yield event
                else:
                    async for event in target_stream:
                        event.author = route
                        yield event
                        
                # Agentic Resilience: Auto-Reroute Simulation
                if route == "booking_simulation":
                    output = ctx.session.state.get("booking_details", "{}")
                    try:
                        booking_res = json.loads(output)
                        if booking_res.get("error") and "failed_provider_id" in booking_res:
                            failed_id = booking_res["failed_provider_id"]
                            excluded = json.loads(ctx.session.state.get("excluded_providers", "[]"))
                            if failed_id not in excluded: excluded.append(failed_id)
                            ctx.session.state["excluded_providers"] = json.dumps(excluded)
                            
                            # Reroute to matcher
                            target_stream = self._worker_agents["discovery_match"].run(ctx)
                            if hasattr(target_stream, '__aenter__'):
                                async with target_stream as stream:
                                    async for event in stream:
                                        event.author = "discovery_match"
                                        yield event
                            else:
                                async for event in target_stream:
                                    event.author = "discovery_match"
                                    yield event
                                    
                            # Continue loop to try booking_simulation again!
                            continue
                    except Exception as e:
                        pass
                
                # If discovery_match was run and auto-booking is requested/appropriate, we could loop here
                if route == "discovery_match":
                    pass
            
            break # Exit retry loop if successful
            
        # If direct_response, we do nothing more, the planner's output serves as the response.

supervisor_agent = AntigravitySupervisorAgent()
