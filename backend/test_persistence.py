import pytest
import json
import uuid
import os
from fastapi.testclient import TestClient

from app.main import app, supabase_client
from app.config import settings
from app.services.semantic_understanding import SemanticUnderstanding, Intent, ProductFamily, RiskLevel

client = TestClient(app)

from tests.integration_env_guard import verify_staging_environment

def test_live_semantic_payload_persistence():
    verify_staging_environment()
    session_id = f"test-semantic-persistence-{uuid.uuid4()}"
    store_id = "hoverboard_store"
    
    # Mock SemanticUnderstanding payload
    mock_sem = SemanticUnderstanding(
        intent=Intent.power_issue,
        sub_intent="power_issue",
        product_family=ProductFamily.electric_scooter,
        product_entity="x2 scooter",
        issue_category="charging",
        risk_level=RiskLevel.low,
        customer_goal="power_issue",
        age_context="adult",
        order_specific=False,
        needs_clarification=False,
        clarification_reason="",
        confidence=0.98
    )
    
    try:
        # Mock generate_support_reply and analyze_semantics just for this post
        from unittest.mock import patch
        with patch("app.services.support_brain.generate_support_reply") as mock_brain:
            with patch("app.services.semantic_understanding.analyze_semantics") as mock_analyze:
                mock_analyze.return_value = mock_sem
                
                mock_brain.return_value = {
                    "reply_text": "Here is how to check your charger.",
                    "should_escalate": False,
                    "intent": "power_issue",
                    "confidence": 0.98,
                    "escalation_reason": "",
                    "brain_mode": "minimax",
                    "source_used": "General Support Fallback"
                }
                
                response = client.post(
                    "/api/chat",
                    json={
                        "message": "my x2 scooter stop work charger green but no turn",
                        "store_id": store_id,
                        "conversation_id": session_id
                    }
                )
                
                assert response.status_code == 200, f"Failed to post chat: {response.text}"
                
        # Now verify from the live Supabase Staging DB
        res = supabase_client.table("chat_logs").select("*").eq("session_id", session_id).execute()
        assert len(res.data) > 0, "Row was not written to Supabase"
        
        row = res.data[0]
        
        # Verify matched_source
        assert row["matched_source"] == "General Support Fallback"
        
        # Verify semantic_metadata
        meta = row["semantic_metadata"]
        assert meta is not None
        assert type(meta) == dict
        
        # Assert every required field is present
        assert meta.get("semantic_intent") == "power_issue"
        assert meta.get("semantic_sub_intent") == "power_issue"
        assert meta.get("semantic_product_family") == "electric_scooter"
        assert meta.get("semantic_product_entity") == "x2 scooter"
        assert meta.get("semantic_issue_category") == "charging"
        assert meta.get("semantic_risk_level") == "low"
        assert meta.get("semantic_customer_goal") == "power_issue"
        assert meta.get("semantic_age_context") == "adult"
        assert meta.get("semantic_order_specific") is False
        assert meta.get("semantic_needs_clarification") is False
        assert meta.get("semantic_clarification_reason") == ""
        assert meta.get("semantic_confidence") == 0.98
        
        # Check lengths
        serialized = json.dumps(meta)
        print(f"\nSerialized semantic payload length: {len(serialized)}")
        assert len(serialized) > 255, "Payload must be strictly greater than 255 to prove we bypassed the truncation limit"
        
        # Verify API / Dashboard read compatibility
        dash_res = client.get("/api/conversations")
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        
        found = next((c for c in dash_data.get("logs", []) if c["session_id"] == session_id), None)
        if not found:
            print("COULD NOT FIND SESSION:", session_id)
            print("NUM RETURNED:", len(dash_data.get("logs", [])))
            for c in dash_data.get("logs", [])[:5]:
                print(c.get("session_id"))
        assert found is not None, "Test session not returned by dashboard API"
        assert found["brain_mode"] == "MINIMAX_STRUCTURED"
        assert found["matched_source"] == "General Support Fallback"
        assert found["intent"] == "power_issue"

    finally:
        # Cleanup
        supabase_client.table("chat_logs").delete().eq("session_id", session_id).execute()
        
        # Verify cleanup
        verify_cleanup = supabase_client.table("chat_logs").select("*").eq("session_id", session_id).execute()
        assert len(verify_cleanup.data) == 0, "Test row cleanup failed"
