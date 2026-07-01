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
    print("\nALL AUTO-ESCALATION INTEGRATION TESTS PASSED SUCCESSFULLY! ✅")

if __name__ == "__main__":
    try:
        test_integration_flow()
        test_auto_escalation()
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e} ❌")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e} ❌")
        sys.exit(1)
