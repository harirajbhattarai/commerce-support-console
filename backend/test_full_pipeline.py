import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
import json

client = TestClient(app)

def run_chat(message: str, session_id: str):
    # ensure admin token is set
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
        
    res = client.post("/api/chat", json={
        "store_id": "hoverboard_store",
        "message": message,
        "conversation_id": session_id
    })
    
    # fetch logs to get real status
    conv_res = client.get("/api/conversations", headers={"X-Admin-Token": admin_token})
    session_log = next((log for log in conv_res.json().get("logs", []) if log["session_id"] == session_id), None)
    
    return {
        "reply": res.json()["reply"],
        "escalated": session_log["escalated"] if session_log else False,
        "effective_status": session_log["status"] if session_log else "unknown",
        "routing_reason": session_log.get("escalation_reason", "") if session_log else ""
    }

def delete_session(session_id: str):
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    try:
        client.delete(f"/api/conversations/{session_id}", headers={"X-Admin-Token": admin_token})
    except Exception as e:
        print(f"Cleanup failed for {session_id}: {e}")

def test_full_pipeline_negative_controls():
    queries = [
        "fire red colour hoverboard",
        "smoke grey colour hoverboard",
        "spark design hoverboard",
        "hot-selling hoverboard",
        "fire pattern hoverboard",
        "a person is buying this for a child",
        "Personal Light Electric Vehicle rules",
        "someone is buying this for my child",
        "someone told me this hoverboard is blue",
        "this is for someone aged 12",
        "my child is 9 years old"
    ]
    
    for q in queries:
        session_id = f"test-full-pipeline-neg-{uuid.uuid4()}"
        try:
            res = run_chat(q, session_id)
            assert res["escalated"] == False, f"'{q}' falsely escalated! Status: {res['effective_status']}"
            assert res["effective_status"] != "needs_escalation", f"'{q}' falsely has needs_escalation status"
            assert "stop using" not in res["reply"].lower(), f"'{q}' falsely served stop-use safety answer!"
        finally:
            delete_session(session_id)

def test_full_pipeline_positive_controls():
    queries = [
        "my hoverboard is burn",
        "smoke coming from my hoverboard",
        "sparks coming from charger",
        "battery is swollen",
        "hoverboard is extremely hot",
        "my hoverboard smells burnt",
        "i want talk to person",
        "can i talk to someone",
        "human please",
        "speak to advisor",
        "i need someone from support"
    ]
    for q in queries:
        session_id = f"test-full-pipeline-pos-{uuid.uuid4()}"
        try:
            res = run_chat(q, session_id)
            assert res["escalated"] == True, f"'{q}' failed to escalate!"
            assert res["effective_status"] == "needs_escalation", f"'{q}' wrong status: {res['effective_status']}"
        finally:
            delete_session(session_id)

def test_full_pipeline_mixed_safety_human():
    q = "my hoverboard smells and I want to talk to a person"
    session_id = f"test-full-pipeline-mixed-{uuid.uuid4()}"
    try:
        res = run_chat(q, session_id)
        assert res["escalated"] == True
        assert res["effective_status"] == "needs_escalation"
        assert "stop using" in res["reply"].lower(), "Safety response must override human handoff"
    finally:
        delete_session(session_id)

def test_metadata_boundary_controls():
    # Inject test mock articles into the local knowledge_base
    from app.main import knowledge_base
    
    test_articles = [
        # Scenario A: Title contains "Safety" but metadata is not high risk.
        # Should NOT classify as critical solely from title.
        {
            "title": "UKCA and CE Safety Certification",
            "keywords": ["certification", "ukca", "ce"],
            "content": "Our hoverboards meet UKCA safety standards.",
            "risk_level": "low",
            "human_review_required": False
        },
        # Scenario B & C: High-risk article (title doesn't matter)
        # Should NOT serve as normal auto-reply for a safe query.
        {
            "title": "Critical Battery Instructions",
            "keywords": ["fire", "red", "battery", "critical"],
            "content": "Stop using immediately if smoking.",
            "risk_level": "high",
            "human_review_required": True
        }
    ]
    
    import app.main
    original_client = app.main.supabase_client
    app.main.supabase_client = None
    
    original_articles = list(knowledge_base["hoverboard_store"])
    knowledge_base["hoverboard_store"] = test_articles
    
    try:
        # Run test for Scenario A & D
        # We query "ukca safety fire red" -> matches Scenario A
        # The query is safe (no device context + smell/hot, and "fire red" bypasses critical gate)
        q_safe_a = "ukca safety fire red colour hoverboard"
        session_a = f"test-meta-a-{uuid.uuid4()}"
        try:
            res_a = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q_safe_a,
                "conversation_id": session_a
            })
            # It should return the safe article, NOT escalate, and NOT block it.
            assert "UKCA" in res_a.json()["reply"], "Did not serve safe article with 'Safety' in title!"
        finally:
            delete_session(session_a)

        # Run test for Scenario B & C
        # We query "critical battery fire red" -> matches Scenario B/C
        # The query is safe ("fire red", "battery" is context but no smell/hot)
        q_safe_b = "critical battery instructions fire red colour hoverboard"
        session_b = f"test-meta-b-{uuid.uuid4()}"
        try:
            res_b = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q_safe_b,
                "conversation_id": session_b
            })
            # It should block the high-risk article and return a fallback!
            assert "Stop using immediately" not in res_b.json()["reply"], "Falsely served high-risk article!"
            assert "General guidelines" in res_b.json()["reply"] or "contact@hoverboardstore.co.uk" in res_b.json()["reply"], "Should return general rules fallback."
        finally:
            delete_session(session_b)
    finally:
        # Cleanup mock data
        knowledge_base["hoverboard_store"] = original_articles
        app.main.supabase_client = original_client
