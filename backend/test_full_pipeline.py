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
    import uuid

    test_articles = [
        # Scenario A: Title contains "Safety" but metadata is not high risk.
        # Expected: not critical
        {
            "title": "UKCA and CE Safety Certification",
            "keywords": ["ukca_safety_test"],
            "content": "Our hoverboards meet UKCA safety standards.",
            "risk_level": "low",
            "human_review_required": False
        },
        # Scenario B: High-risk article (title doesn't matter)
        # Expected: critical
        {
            "title": "Critical Battery and Charging — Stop Use Immediately",
            "keywords": ["critical_battery_test"],
            "content": "Stop using immediately if smoking.",
            "risk_level": "high",
            "human_review_required": True
        },
        # Scenario C: Title contains "Safety" but has no structured metadata and no approved classification
        # Expected: UNKNOWN / UNCLASSIFIED (so not served directly)
        {
            "title": "General Riding Safety Tips",
            "keywords": ["riding_safety_test"],
            "content": "Wear a helmet when riding."
        },
        # Scenario D: Title contains no safety/hazard words and no metadata
        # Expected: UNKNOWN / UNCLASSIFIED (so not served directly)
        {
            "title": "Basic Maintenance Guide",
            "keywords": ["basic_maintenance_test"],
            "content": "Clean your hoverboard regularly."
        }
    ]
    
    import app.main
    original_client = app.main.supabase_client
    app.main.supabase_client = None
    
    original_articles = list(knowledge_base["hoverboard_store"])
    knowledge_base["hoverboard_store"] = test_articles
    
    session_a = None
    session_b = None
    session_c = None
    session_d = None
    
    try:
        # A. Safe query -> UKCA article. Should NOT block it.
        q_a = "what is the ukca_safety_test for hoverboard"
        session_a = f"test-meta-a-{uuid.uuid4()}"
        res_a = client.post("/api/chat", json={"store_id": "hoverboard_store", "message": q_a, "conversation_id": session_a})
        assert "UKCA" in res_a.json()["reply"], "Did not serve safe article with 'Safety' in title!"
        
        # B. Safe query -> High risk article. Should BLOCK it.
        q_b = "what are the critical_battery_test instructions"
        session_b = f"test-meta-b-{uuid.uuid4()}"
        res_b = client.post("/api/chat", json={"store_id": "hoverboard_store", "message": q_b, "conversation_id": session_b})
        assert "Stop using immediately" not in res_b.json()["reply"], "Falsely served high-risk article directly!"
        
        # C. Safe query -> Unknown legacy article with 'Safety' in title. Should BLOCK it.
        q_c = "what are the riding_safety_test rules"
        session_c = f"test-meta-c-{uuid.uuid4()}"
        res_c = client.post("/api/chat", json={"store_id": "hoverboard_store", "message": q_c, "conversation_id": session_c})
        assert "Wear a helmet" not in res_c.json()["reply"], "Falsely served unknown legacy article with 'Safety' in title directly!"
        
        # D. Safe query -> Unknown legacy article with NO 'Safety' in title. Should BLOCK it.
        q_d = "what is the basic_maintenance_test guide"
        session_d = f"test-meta-d-{uuid.uuid4()}"
        res_d = client.post("/api/chat", json={"store_id": "hoverboard_store", "message": q_d, "conversation_id": session_d})
        assert "Clean your hoverboard" not in res_d.json()["reply"], "Falsely served unknown legacy article directly!"
        
    finally:
        # Cleanup mock data
        knowledge_base["hoverboard_store"] = original_articles
        app.main.supabase_client = original_client
        
        # Cleanup generated sessions
        if session_a:
            delete_session(session_a)
        if session_b:
            delete_session(session_b)
        if session_c:
            delete_session(session_c)
        if session_d:
            delete_session(session_d)
