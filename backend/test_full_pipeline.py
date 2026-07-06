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
        "this product is hot-selling",
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
        finally:
            delete_session(session_id)

def test_full_pipeline_positive_controls():
    queries = [
        "my hoverboard is burn",
        "my hoverboard smells burnt",
        "smoke coming from my board",
        "battery is swollen",
        "sparks coming from my charger",
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
    q = "i need an agent my hoverboard smells burnt"
    session_id = f"test-full-pipeline-mix-{uuid.uuid4()}"
    try:
        res = run_chat(q, session_id)
        assert res["escalated"] == True, f"'{q}' failed to escalate!"
        assert res["effective_status"] == "needs_escalation", f"'{q}' wrong status: {res['effective_status']}"
        assert "safety" in res["routing_reason"].lower() or "critical" in res["routing_reason"].lower() or "battery" in res["routing_reason"].lower() or "smell" in res["routing_reason"].lower(), f"Safety should be primary routing reason. Reason: {res['routing_reason']}"
    finally:
        delete_session(session_id)
