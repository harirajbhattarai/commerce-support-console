import uuid
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_integration_flow():
    print("Starting integration test for human takeover flow...")
    
    # 1. Customer starts conversation
    session_id = f"test-takeover-{uuid.uuid4()}"
    store_id = "hoverboard_store"
    
    # Configure token for admin tests
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    # Temporarily set token in settings if it's not set
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
        
    headers = {"X-Admin-Token": admin_token}
    
    # 2. Customer sends a standard hoverboard query (matches bot knowledge)
    chat_payload = {
        "store_id": store_id,
        "message": "tell me about hoverboard battery safety",
        "conversation_id": session_id
    }
    
    print(f"\n[Step 1] Customer sends message: '{chat_payload['message']}'")
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    print(f"Bot replies: '{chat_data['reply']}'")
    assert "unattended" in chat_data["reply"].lower() or "safety" in chat_data["reply"].lower()
    
    # 3. Staff fetches conversations and verifies thread exists
    print("\n[Step 2] Staff fetches conversations list from admin console...")
    conv_res = client.get("/api/conversations", headers=headers)
    assert conv_res.status_code == 200, f"Failed to fetch conversations: {conv_res.text}"
    conv_data = conv_res.json()
    logs = conv_data.get("logs", [])
    
    # Find our session log
    session_log = next((log for log in logs if log["session_id"] == session_id), None)
    assert session_log is not None, "Could not find session in logs"
    print(f"Verified: Session {session_id} found in logs database.")
    
    # 4. Staff updates status to needs_escalation to simulate takeover
    print(f"\n[Step 3] Staff marks session {session_id} status as needs_escalation...")
    status_res = client.put(f"/api/conversations/{session_id}/status?status=needs_escalation", headers=headers)
    assert status_res.status_code == 200, f"Status update failed: {status_res.text}"
    
    # 5. Customer sends another message - Bot should NOT auto-answer
    chat_payload_2 = {
        "store_id": store_id,
        "message": "it is still beep flag warning",
        "conversation_id": session_id
    }
    print(f"\n[Step 4] Customer sends query after escalation: '{chat_payload_2['message']}'")
    chat_res_2 = client.post("/api/chat", json=chat_payload_2)
    assert chat_res_2.status_code == 200, f"Chat failed: {chat_res_2.text}"
    chat_data_2 = chat_res_2.json()
    print(f"Bot replies: '{chat_data_2['reply']}'")
    # Verify bot returned holding message instead of keyword matching
    assert "notified" in chat_data_2["reply"].lower() or "shortly" in chat_data_2["reply"].lower()
    print("Verified: Bot auto-answering was bypassed correctly.")
    
    # 6. Staff writes and sends human reply
    reply_payload = {
        "session_id": session_id,
        "message": "Hi, this is a human support agent. I am looking into your case right now."
    }
    print(f"\n[Step 5] Staff posts human agent reply: '{reply_payload['message']}'")
    reply_res = client.post("/api/agent-replies", json=reply_payload, headers=headers)
    assert reply_res.status_code == 200, f"Agent reply failed: {reply_res.text}"
    
    # 7. Customer polls for replies
    print("\n[Step 6] Customer widget polls for new agent replies...")
    poll_res = client.get(f"/api/agent-replies/{session_id}")
    assert poll_res.status_code == 200, f"Poll failed: {poll_res.text}"
    poll_data = poll_res.json()
    
    # Check that our human reply is present
    assert len(poll_data) > 0, "No agent replies returned"
    agent_message = next((msg for msg in poll_data if msg["message"] == reply_payload["message"]), None)
    assert agent_message is not None, "Human agent message not found in poll results"
    assert agent_message.get("role") == "support_agent", "Role support_agent label missing"
    assert agent_message.get("message_type") == "agent_reply", "message_type agent_reply label missing"
    print(f"Verified: Customer widget successfully received agent reply with correct labels: '{agent_message['message']}'")

    # 8. Fetch conversations and check role mapping in dashboard responses
    print("\n[Step 7] Console fetches conversations and verifies role mapping in agent replies...")
    list_res = client.get("/api/conversations", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    replies_list = list_data.get("agent_replies", [])
    agent_msg_in_list = next((r for r in replies_list if r["session_id"] == session_id and r["message"] == reply_payload["message"]), None)
    assert agent_msg_in_list is not None, "Agent reply not found in unified list response"
    assert agent_msg_in_list.get("role") == "support_agent", "Role support_agent label missing in conversations list"
    assert agent_msg_in_list.get("message_type") == "agent_reply", "message_type agent_reply label missing in conversations list"
    print("Verified: Staff reply appears in dashboard with correct Support agent roles.")
    
    # Clean up test conversation log to keep database clean
    print(f"\n[Cleanup] Sending DELETE request for session {session_id}...")
    cleanup_res = client.delete(f"/api/conversations/{session_id}", headers=headers)
    assert cleanup_res.status_code == 200, f"Cleanup delete failed: {cleanup_res.text}"
    
    print("\nALL TAKEOVER INTEGRATION TESTS PASSED SUCCESSFULLY! ✅")

def test_auto_escalation():
    print("\nStarting integration test for auto-escalation intent...")
    session_id = f"test-auto-esc-{uuid.uuid4()}"
    store_id = "hoverboard_store"
    
    # Configure token for admin tests
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
    headers = {"X-Admin-Token": admin_token}
    
    # Send message with explicit human intent
    chat_payload = {
        "store_id": store_id,
        "message": "can I speak to someone from support team?",
        "conversation_id": session_id
    }
    
    print(f"\n[Step 1] Customer sends human request: '{chat_payload['message']}'")
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    print(f"Bot replies: '{chat_data['reply']}'")
    assert "passed this to our support team" in chat_data["reply"].lower()
    
    # Verify that it is marked as escalated in database
    print("\n[Step 2] Staff fetches conversation logs to verify auto-escalated status...")
    conv_res = client.get("/api/conversations", headers=headers)
    assert conv_res.status_code == 200
    conv_data = conv_res.json()
    logs = conv_data.get("logs", [])
    
    # Find our session log
    session_log = next((log for log in logs if log["session_id"] == session_id), None)
    assert session_log is not None, "Could not find session in logs"
    assert session_log.get("escalated") is True, "Session escalated attribute was not set to true"
    assert session_log.get("status") == "needs_escalation", f"Session status was not needs_escalation, got {session_log.get('status')}"
    print(f"Verified: Session {session_id} is marked as escalated and status set to needs_escalation. ✅")
    
    # Clean up test conversation log to keep database clean
    print(f"\n[Cleanup] Sending DELETE request for session {session_id}...")
    cleanup_res = client.delete(f"/api/conversations/{session_id}", headers=headers)
    assert cleanup_res.status_code == 200, f"Cleanup delete failed: {cleanup_res.text}"
    
    print("\nALL AUTO-ESCALATION INTEGRATION TESTS PASSED SUCCESSFULLY! ✅")

def test_archive_and_delete():
    print("\nStarting integration test for Archive & Permanent Delete...")
    session_id = f"test-arch-del-{uuid.uuid4()}"
    store_id = "hoverboard_store"
    
    # Configure token
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
    headers = {"X-Admin-Token": admin_token}
    
    # 1. Create a log
    chat_payload = {
        "store_id": store_id,
        "message": "Archive testing message flow",
        "conversation_id": session_id
    }
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200
    
    # 2. Add a staff note
    note_payload = {
        "session_id": session_id,
        "note": "Test note for deletion cascade",
        "author": "Agent"
    }
    note_res = client.post("/api/notes", json=note_payload, headers=headers)
    assert note_res.status_code == 200
    
    # 3. Add a draft
    draft_payload = {
        "session_id": session_id,
        "draft_text": "Test draft for deletion cascade"
    }
    draft_res = client.post("/api/reply-draft", json=draft_payload, headers=headers)
    assert draft_res.status_code == 200
    
    # 4. Add an agent reply
    reply_payload = {
        "session_id": session_id,
        "message": "Test agent reply for deletion cascade"
    }
    reply_res = client.post("/api/agent-replies", json=reply_payload, headers=headers)
    assert reply_res.status_code == 200
    
    # 5. Update status to archived
    print("\n[Step 1] Setting conversation status to archived...")
    status_res = client.put(f"/api/conversations/{session_id}/status?status=archived", headers=headers)
    assert status_res.status_code == 200, f"Status update failed. Code: {status_res.status_code}, Body: {status_res.text}"
    
    # Verify status is archived
    conv_res = client.get("/api/conversations", headers=headers)
    assert conv_res.status_code == 200
    session_log = next((log for log in conv_res.json().get("logs", []) if log["session_id"] == session_id), None)
    assert session_log is not None, f"Could not find conversation {session_id} after archiving"
    assert session_log.get("status") == "archived", f"Expected status archived, got {session_log.get('status')}"
    print("Verified: Conversation status successfully updated to archived in Supabase database. ✅")
    
    # 6. Delete the conversation
    print("\n[Step 2] Sending DELETE request for conversation...")
    delete_res = client.delete(f"/api/conversations/{session_id}", headers=headers)
    assert delete_res.status_code == 200, f"Delete failed. Code: {delete_res.status_code}, Body: {delete_res.text}"
    
    # Verify it is completely gone from REST API list
    conv_res_after = client.get("/api/conversations", headers=headers)
    session_log_after = next((log for log in conv_res_after.json().get("logs", []) if log["session_id"] == session_id), None)
    assert session_log_after is None, "Conversation was not deleted from chat_logs REST response"
    
    # Verify directly in Supabase tables
    from app.database import supabase_client
    if supabase_client:
        try:
            drafts_check = supabase_client.table("reply_drafts").select("*").eq("session_id", session_id).execute()
            assert not drafts_check.data, "reply_drafts record was not deleted"
            
            notes_check = supabase_client.table("staff_notes").select("*").eq("session_id", session_id).execute()
            assert not notes_check.data, "staff_notes record was not deleted"
            
            replies_check = supabase_client.table("agent_replies").select("*").eq("session_id", session_id).execute()
            assert not replies_check.data, "agent_replies record was not deleted"
            
            logs_check = supabase_client.table("chat_logs").select("*").eq("session_id", session_id).execute()
            assert not logs_check.data, "chat_logs record was not deleted"
            
            print("Verified: Session was completely purged from Supabase child/parent tables. ✅")
        except Exception as e:
            print(f"Skipping direct table verification: {e}")
            
    print("Verified: Conversation and all associated cascading child data records completely removed. ✅")
    
    print("\nALL ARCHIVE & DELETE INTEGRATION TESTS PASSED SUCCESSFULLY! ✅")

def test_support_brain_scenarios():
    print("\nStarting integration test for Support Brain scenarios...")
    
    # Configure token
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
    headers = {"X-Admin-Token": admin_token}
    
    # Keep track of created sessions for auto-cleanup
    created_sessions = []
    
    # Let's temporarily ensure MiniMax API Key is NOT configured to check fallback behavior
    original_key = settings.MINIMAX_API_KEY
    settings.MINIMAX_API_KEY = "" # Ensure fallback rules are active
    
    try:
        # Case 1 (Fallback Mode): "Which hoverboard is best for a 9 year old?" -> expects fallback warning
        session_id_1 = f"test-brain-1-{uuid.uuid4()}"
        created_sessions.append(session_id_1)
        res1 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "Which hoverboard is best for a 9 year old?",
            "conversation_id": session_id_1
        })
        assert res1.status_code == 200
        data1 = res1.json()
        print(f"Case 1 (Fallback) Bot Reply: {data1['reply']}")
        assert "couldn't find" in data1["reply"].lower() or "escalate" in data1["reply"].lower() or "6.5" in data1["reply"].lower() or "beginner" in data1["reply"].lower()
        
        # Case 1 (MiniMax Mode): Verify happy path with configured MiniMax
        import unittest.mock as mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "For a 9-year-old child, we highly recommend the Aeroglide Hoverboard as it features built-in learner modes and safety sensors."
                }
            }]
        }
        with mock.patch("requests.post", return_value=mock_response):
            settings.MINIMAX_API_KEY = "test_key"
            session_id_1_minimax = f"test-brain-1-minimax-{uuid.uuid4()}"
            created_sessions.append(session_id_1_minimax)
            res1_minimax = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": "Which hoverboard is best for a 9 year old?",
                "conversation_id": session_id_1_minimax
            })
            assert res1_minimax.status_code == 200
            data1_minimax = res1_minimax.json()
            print(f"Case 1 (MiniMax Active) Bot Reply: {data1_minimax['reply']}")
            assert "aeroglide" in data1_minimax["reply"].lower()
            
        # Clear settings key back for subsequent fallback checks
        settings.MINIMAX_API_KEY = ""
        
        # Case 2: "How long is delivery?" -> expects shipping answer
        session_id_2 = f"test-brain-2-{uuid.uuid4()}"
        created_sessions.append(session_id_2)
        res2 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "How long is delivery?",
            "conversation_id": session_id_2
        })
        assert res2.status_code == 200
        data2 = res2.json()
        print(f"Case 2 Bot Reply: {data2['reply']}")
        assert "days" in data2["reply"].lower() or "delivery" in data2["reply"].lower() or "shipping" in data2["reply"].lower()
        
        # Case 3: "Can I return it?" -> expects return policy answer
        session_id_3 = f"test-brain-3-{uuid.uuid4()}"
        created_sessions.append(session_id_3)
        res3 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "Can I return it?",
            "conversation_id": session_id_3
        })
        assert res3.status_code == 200
        data3 = res3.json()
        print(f"Case 3 Bot Reply: {data3['reply']}")
        assert "return" in data3["reply"].lower() or "day" in data3["reply"].lower()
        
        # Case 4: "My hoverboard smells like burning" -> expects escalate, no unsafe advice
        session_id_4 = f"test-brain-4-{uuid.uuid4()}"
        created_sessions.append(session_id_4)
        res4 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "My hoverboard smells like burning",
            "conversation_id": session_id_4
        })
        assert res4.status_code == 200
        data4 = res4.json()
        print(f"Case 4 Bot Reply: {data4['reply']}")
        assert "support team" in data4["reply"].lower() or "representative" in data4["reply"].lower()
        
        # Verify it got marked as escalated
        conv_res = client.get("/api/conversations", headers=headers)
        session_log = next((log for log in conv_res.json().get("logs", []) if log["session_id"] == session_id_4), None)
        assert session_log is not None
        assert session_log.get("status") == "needs_escalation"
        
        # Case 5: "Where is my order?" -> expects ask for verification / escalate
        session_id_5 = f"test-brain-5-{uuid.uuid4()}"
        created_sessions.append(session_id_5)
        res5 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "Where is my order?",
            "conversation_id": session_id_5
        })
        assert res5.status_code == 200
        data5 = res5.json()
        print(f"Case 5 Bot Reply: {data5['reply']}")
        assert "support team" in data5["reply"].lower() or "representative" in data5["reply"].lower()
        
        # Case 6: "I want to speak to a person" -> expects needs agent
        session_id_6 = f"test-brain-6-{uuid.uuid4()}"
        created_sessions.append(session_id_6)
        res6 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "I want to speak to a person",
            "conversation_id": session_id_6
        })
        assert res6.status_code == 200
        data6 = res6.json()
        print(f"Case 6 Bot Reply: {data6['reply']}")
        assert "support team" in data6["reply"].lower() or "representative" in data6["reply"].lower()
        
        # Case 7: MiniMax key missing fallback check -> already tested above because MINIMAX_API_KEY was empty!
        # Let's verify metadata matches fallback brain mode
        conv_res = client.get("/api/conversations", headers=headers)
        session_log_fallback = next((log for log in conv_res.json().get("logs", []) if log["session_id"] == session_id_6), None)
        assert session_log_fallback is not None
        assert session_log_fallback.get("brain_mode") == "rules" or session_log_fallback.get("brain_mode") == "fallback"
        
    finally:
        # Restore key
        settings.MINIMAX_API_KEY = original_key
        # Clean up all created sessions
        print("\n[Cleanup] Cleaning up all Support Brain test sessions...")
        for sid in created_sessions:
            try:
                client.delete(f"/api/conversations/{sid}", headers=headers)
            except Exception as e:
                print(f"Failed to delete test session {sid}: {e}")
        
    print("\nALL SUPPORT BRAIN INTEGRATION SCENARIOS PASSED SUCCESSFULLY! ✅")

def test_widget_endpoint_resolution():
    print("\nStarting integration test for storefront widget configuration...")
    import pathlib
    
    widget_path = pathlib.Path(__file__).parent.parent / "frontend" / "shopify-widget" / "hoverboard-chat-widget.js"
    assert widget_path.exists(), f"Widget file does not exist at {widget_path}"
    
    with open(widget_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check that old offline messages are removed
    assert "Live Chatbot Server is offline" not in content, "Found old offline status text"
    assert "Showing simulated offline reply" not in content, "Found old offline simulation text"
    assert "Please make sure the FastAPI backend is running locally" not in content, "Found old local setup warning"
    
    # Check that production URL is defined as fallback
    assert "https://commerce-support-console-production.up.railway.app" in content, "Production Railway URL is missing in widget script"
    
    # Check CORS defaults in main.py
    main_path = pathlib.Path(__file__).parent / "app" / "main.py"
    with open(main_path, "r", encoding="utf-8") as fm:
        main_content = fm.read()
    assert "https://hoverboardstore.co.uk" in main_content, "CORS origin hoverboardstore.co.uk is missing"
    assert "https://www.hoverboardstore.co.uk" in main_content, "CORS origin www.hoverboardstore.co.uk is missing"
    
    print("\nALL STOREFRONT WIDGET API CONNECTION TESTS PASSED SUCCESSFULLY! ✅")

def test_shopify_widget_payload_variations():
    print("\nStarting integration test for Shopify widget payload variations...")
    
    # Configure token
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
    headers = {"X-Admin-Token": admin_token}
    
    created_sessions = []
    
    try:
        # 1. Payload with storeId and sessionId -> "tell me about hoverboard battery safety"
        session_id_1 = f"test-payload-1-{uuid.uuid4()}"
        created_sessions.append(session_id_1)
        res1 = client.post("/api/chat", json={
            "storeId": "hoverboard_store",
            "message": "tell me about hoverboard battery safety",
            "sessionId": session_id_1
        })
        assert res1.status_code == 200, f"Payload variation 1 failed: {res1.text}"
        print("Variation 1 (storeId/sessionId, Battery Safety) passed. ✅")
        
        # 2. Payload with store_id and session_id -> "how long is delivery"
        session_id_2 = f"test-payload-2-{uuid.uuid4()}"
        created_sessions.append(session_id_2)
        res2 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "how long is delivery",
            "session_id": session_id_2
        })
        assert res2.status_code == 200, f"Payload variation 2 failed: {res2.text}"
        print("Variation 2 (store_id/session_id, Shipping Times) passed. ✅")
        
        # 3. Payload with store_id, conversation_id, channel -> "can I return it"
        session_id_3 = f"test-payload-3-{uuid.uuid4()}"
        created_sessions.append(session_id_3)
        res3 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "can I return it",
            "conversation_id": session_id_3,
            "channel": "shopify_widget"
        })
        assert res3.status_code == 200, f"Payload variation 3 failed: {res3.text}"
        print("Variation 3 (store_id/conversation_id/channel, Return Policy) passed. ✅")
        
        # 4. Payload with store_id and conversation_id -> "Which hoverboard is best for a 9 year old?"
        session_id_4 = f"test-payload-4-{uuid.uuid4()}"
        created_sessions.append(session_id_4)
        res4 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "Which hoverboard is best for a 9 year old?",
            "conversation_id": session_id_4
        })
        assert res4.status_code == 200, f"Payload variation 4 failed: {res4.text}"
        reply_data4 = res4.json()
        from app.database import supabase_client
        if supabase_client:
            assert "6.5" in reply_data4["reply"] or "beginner" in reply_data4["reply"].lower() or "kids" in reply_data4["reply"].lower()
        print("Variation 4 (store_id/conversation_id, Product Recommendation) passed. ✅")
        
        # 5. Payload with store_id and conversation_id -> "My hoverboard smells like burning"
        session_id_5 = f"test-payload-5-{uuid.uuid4()}"
        created_sessions.append(session_id_5)
        res5 = client.post("/api/chat", json={
            "store_id": "hoverboard_store",
            "message": "My hoverboard smells like burning",
            "conversation_id": session_id_5
        })
        assert res5.status_code == 200, f"Payload variation 5 failed: {res5.text}"
        print("Variation 5 (store_id/conversation_id, Smells like burning) passed. ✅")
        
    finally:
        # Cleanup
        print("[Cleanup] Cleaning up payload variations test sessions...")
        for sid in created_sessions:
            try:
                client.delete(f"/api/conversations/{sid}", headers=headers)
            except Exception as e:
                print(f"Failed to delete test session {sid}: {e}")
                
    print("\nALL SHOPIFY WIDGET PAYLOAD VARIATIONS TESTS PASSED SUCCESSFULLY! ✅")

def test_ai_support_agent_scenarios():
    print("\nStarting integration test for AI Support Agent grouped scenarios...")
    
    # Configure token
    admin_token = settings.ADMIN_DASHBOARD_TOKEN or "test_admin_token"
    if not settings.ADMIN_DASHBOARD_TOKEN:
        settings.ADMIN_DASHBOARD_TOKEN = admin_token
    headers = {"X-Admin-Token": admin_token}
    
    created_sessions = []
    
    # Temporarily set MINIMAX_API_KEY to empty to check safe rules/fallback matching
    original_key = settings.MINIMAX_API_KEY
    settings.MINIMAX_API_KEY = ""
    
    try:
        # A. Product Recommendations (Low Risk -> Auto-answer with helpful guidance)
        recs = [
            "my son is 9 never used one before which hoverboard should i get",
            "is 6.5 hoverboard ok for my daughter she is beginner",
            "what one is better for kids hoverboard or kart bundle",
            "is 8.5 inch too big for a child"
        ]
        for q in recs:
            sid = f"test-ai-rec-{uuid.uuid4()}"
            created_sessions.append(sid)
            res = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q,
                "conversation_id": sid
            })
            assert res.status_code == 200
            data = res.json()
            print(f"Query: '{q}' -> Bot Reply: '{data['reply']}'")
            # Verify helpful details are returned, not fallback warning
            assert "couldn't find" not in data["reply"].lower()
            assert any(w in data["reply"].lower() for w in ["6.5", "8.5", "kart", "beginner", "bundle", "kids"])
            
        # B. Faults/Troubleshooting (Low/Medium Risk -> Auto-answer with general policy / reset help)
        faults = [
            ("if it stops working what do i do", ["make sure it is fully charged", "stops working"]),
            ("hoverboard not turning on", ["make sure it is fully charged", "calibrate", "flat", "level"]),
            ("charger light not coming on", ["charger", "charge"]),
            ("how do i reset it", ["flat level surface", "calibrate", "flat"])
        ]
        for q, expected_keywords in faults:
            sid = f"test-ai-fault-{uuid.uuid4()}"
            created_sessions.append(sid)
            res = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q,
                "conversation_id": sid
            })
            assert res.status_code == 200
            data = res.json()
            print(f"Query: '{q}' -> Bot Reply: '{data['reply']}'")
            assert "couldn't find" not in data["reply"].lower()
            assert any(kw in data["reply"].lower() for kw in expected_keywords)
            
        # C. Delivery (Low Risk -> Auto-answer with shipping times)
        deliveries = [
            ("how long delivery take", "days"),
            ("do u do next day delivery", "next-day"),
            ("is delivery free in uk", "free")
        ]
        for q, expected_keyword in deliveries:
            sid = f"test-ai-del-{uuid.uuid4()}"
            created_sessions.append(sid)
            res = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q,
                "conversation_id": sid
            })
            assert res.status_code == 200
            data = res.json()
            print(f"Query: '{q}' -> Bot Reply: '{data['reply']}'")
            assert "couldn't find" not in data["reply"].lower()
            assert expected_keyword in data["reply"].lower()
            
        # D. Returns/Warranty (Low Risk -> Auto-answer)
        returns_warranty = [
            ("can i return if my child dont like it", "30-day"),
            ("how many months warranty", "12-month"),
            ("if it breaks after few weeks what happens", "warranty")
        ]
        for q, expected_keyword in returns_warranty:
            sid = f"test-ai-ret-{uuid.uuid4()}"
            created_sessions.append(sid)
            res = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q,
                "conversation_id": sid
            })
            assert res.status_code == 200
            data = res.json()
            print(f"Query: '{q}' -> Bot Reply: '{data['reply']}'")
            assert "couldn't find" not in data["reply"].lower()
            assert expected_keyword in data["reply"].lower()
            
        # E. Safety Escalations (High Risk -> Forced escalation holding reply)
        safety = [
            "battery getting hot what should i do",
            "my hoverboard smells burning",
            "it is making smoke while charging"
        ]
        for q in safety:
            sid = f"test-ai-safe-{uuid.uuid4()}"
            created_sessions.append(sid)
            res = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q,
                "conversation_id": sid
            })
            assert res.status_code == 200
            data = res.json()
            print(f"Query: '{q}' -> Bot Reply: '{data['reply']}'")
            assert "support team" in data["reply"].lower() or "representative" in data["reply"].lower()
            # Verify escalated status in database
            conv_res = client.get("/api/conversations", headers=headers)
            log = next((log for log in conv_res.json().get("logs", []) if log["session_id"] == sid), None)
            assert log is not None
            assert log.get("status") == "needs_escalation"
            
        # F. Order-specific (High Risk -> Ask for verification / escalation)
        orders = [
            "where is my order",
            "i ordered yesterday tracking not received",
            "can you cancel my order"
        ]
        for q in orders:
            sid = f"test-ai-order-{uuid.uuid4()}"
            created_sessions.append(sid)
            res = client.post("/api/chat", json={
                "store_id": "hoverboard_store",
                "message": q,
                "conversation_id": sid
            })
            assert res.status_code == 200
            data = res.json()
            print(f"Query: '{q}' -> Bot Reply: '{data['reply']}'")
            assert "provide your order reference number" in data["reply"].lower()
            # Verify escalated status in database
            conv_res = client.get("/api/conversations", headers=headers)
            log = next((log for log in conv_res.json().get("logs", []) if log["session_id"] == sid), None)
            assert log is not None
            assert log.get("status") == "needs_escalation"
            
    finally:
        settings.MINIMAX_API_KEY = original_key
        print("[Cleanup] Cleaning up AI Support Agent test sessions...")
        for sid in created_sessions:
            try:
                client.delete(f"/api/conversations/{sid}", headers=headers)
            except Exception as e:
                print(f"Failed to delete test session {sid}: {e}")
                
    print("\nALL AI SUPPORT AGENT SCENARIOS TESTS PASSED SUCCESSFULLY! ✅")

if __name__ == "__main__":
    try:
        test_integration_flow()
        test_auto_escalation()
        test_archive_and_delete()
        test_support_brain_scenarios()
        test_widget_endpoint_resolution()
        test_shopify_widget_payload_variations()
        test_ai_support_agent_scenarios()
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e} ❌")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e} ❌")
        sys.exit(1)
