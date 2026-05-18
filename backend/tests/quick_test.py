"""Quick e2e test for Maahir v2 pipeline."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import requests, json, time

url = "http://localhost:8000/api/chat"
payload = {
    "message": "Mujhe plumber chahiye F-8 mein abhi",
    "session_id": "test-002",
    "language": "auto"
}

print("Sending request to 8-agent pipeline...")
s = time.time()
r = requests.post(url, json=payload, timeout=300)
elapsed = time.time() - s
d = r.json()

print(f"\n{'='*60}")
print(f"STATUS: {r.status_code} | TIME: {elapsed:.1f}s")
print(f"{'='*60}")
print(f"\nRESPONSE: {d.get('response','')[:300]}")
print(f"\nAGENTS ({len(d.get('trace_steps',[]))}):")
for t in d.get("trace_steps", []):
    agent = t.get("agent", "?")
    status = t.get("status", "?")
    dur = t.get("duration_ms", 0)
    summary = t.get("summary", "")[:80]
    reasoning = t.get("reasoning", "")[:80]
    print(f"  {agent:20s} | {status:9s} | {dur:5d}ms | {summary}")
    if reasoning:
        print(f"  {'':20s} | REASONING: {reasoning}")

print(f"\nPROVIDERS: {len(d.get('providers', []))}")
for p in d.get("providers", []):
    print(f"  {p.get('name','?')} ({p.get('business_name','?')}) - Score: {p.get('score',0)} - {p.get('distance_km',0)}km")

if d.get("pricing"):
    pr = d["pricing"]
    print(f"\nPRICING: PKR {pr.get('price_range',{}).get('min',0):,}-{pr.get('price_range',{}).get('max',0):,}")
    for item in pr.get("breakdown", []):
        print(f"  {item.get('component','')}: +PKR {item.get('amount',0)}")

if d.get("booking"):
    b = d["booking"]
    print(f"\nBOOKING: {b.get('id','')} | {b.get('provider_name','')} | {b.get('status','')}")

print(f"\nCLARIFICATION: {d.get('needs_clarification', False)}")
