import json
import os
import pathlib
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.database import supabase_client

app = FastAPI(
    title="Shopify Chatbot MVP Backend",
    description="FastAPI backend utilizing a local JSON knowledge base for multi-store support routing.",
    version="1.0.0"
)

# Enable CORS for local and live deployment dynamically
origins = []
if settings.ALLOWED_ORIGINS:
    origins = [orig.strip() for orig in settings.ALLOWED_ORIGINS.split(",") if orig.strip()]
else:
    origins = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hoverboardstore.co.uk",
        "https://www.hoverboardstore.co.uk"
    ]

# If wildcard is explicitly used, allow_credentials must be False due to browser security restrictions.
allow_all = "*" in origins or (len(origins) == 1 and origins[0] == "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes.knowledge import router as knowledge_router
app.include_router(knowledge_router)

# --------------------------------------------------------------------------
# DATA MODELS
# --------------------------------------------------------------------------
class ChatRequest(BaseModel):
    store_id: Optional[str] = None
    storeId: Optional[str] = None
    message: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    sessionId: Optional[str] = None
    channel: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    store_id: str
    matched_article: Optional[str] = None

class NoteRequest(BaseModel):
    session_id: str
    note: str
    author: str = "Agent"

class DraftRequest(BaseModel):
    session_id: str
    draft_text: str

class ReplyDraftRequest(BaseModel):
    session_id: str
    draft_text: str

class AgentReplyRequest(BaseModel):
    session_id: str
    message: str

class AmazonAnalysisRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    order_id: Optional[str] = None

class AmazonAnalysisResponse(BaseModel):
    session_id: Optional[str] = None
    issue_category: str
    risk_level: str
    recommended_action: str
    suggested_reply: Optional[str] = None
    knowledge_found: bool = False
    knowledge_sources: List[str] = []
    retrieved_context_summary: Optional[str] = None
    human_review_required_from_knowledge: bool = False

# --------------------------------------------------------------------------
# LOAD KNOWLEDGE BASE DATA
# --------------------------------------------------------------------------
DATA_DIR = pathlib.Path(__file__).parent / "data"
KB_FILE_PATH = DATA_DIR / "knowledge_base.json"

knowledge_base: Dict[str, List[dict]] = {}

def load_kb():
    global knowledge_base
    if not KB_FILE_PATH.exists():
        print(f"WARNING: Knowledge base file not found at {KB_FILE_PATH}")
        knowledge_base = {}
        return
    try:
        with open(KB_FILE_PATH, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
            print(f"Successfully loaded knowledge base containing {len(knowledge_base)} stores.")
    except Exception as e:
        print(f"ERROR: Failed to load knowledge base: {e}")
        knowledge_base = {}

# Load on startup
load_kb()

from fastapi import Header, Query, Depends
from fastapi.responses import HTMLResponse
from app.auth import verify_admin_token

@app.get("/admin-dashboard.html", response_class=HTMLResponse)
async def serve_admin_dashboard(token: Optional[str] = None):
    expected_token = settings.ADMIN_DASHBOARD_TOKEN
    if expected_token and token != expected_token:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing admin token.")
        
    admin_file_path = os.path.join(frontend_dir, "admin-dashboard.html") if frontend_dir else None
    if not admin_file_path or not os.path.exists(admin_file_path):
        raise HTTPException(status_code=404, detail="Admin dashboard file not found.")
        
    with open(admin_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/health")
def health_check():
    db_status = "not_configured"
    if supabase_client:
        try:
            # Perform a lightweight query to verify actual database connectivity
            supabase_client.table("stores").select("id").limit(1).execute()
            db_status = "connected"
        except Exception as e:
            db_status = f"connection_failed: {str(e)}"
            
    return {
        "status": "healthy",
        "database": db_status,
        "stores_loaded": list(knowledge_base.keys())
    }


@app.get("/api/brain/health")
async def brain_health():
    api_key_set = bool(settings.MINIMAX_API_KEY and "placeholder" not in settings.MINIMAX_API_KEY and settings.MINIMAX_API_KEY != "")
    return {
        "minimax_configured": api_key_set,
        "fallback_available": True,
        "model_configured": settings.MINIMAX_MODEL
    }

@app.get("/api/test-match")
async def test_match_endpoint(q: str = "Which hoverboard is best for a 9 year old?", store_id: str = "hoverboard_store"):
    store_articles = knowledge_base.get(store_id, [])
    matched_content = None
    matched_title = None
    
    if supabase_client:
        try:
            from app.services.knowledge_service import KnowledgeService
            ret_res = await KnowledgeService.get_support_knowledge(
                query=q,
                store_id=store_id
            )
            if ret_res.get("success"):
                k_list = ret_res.get("knowledge", [])
                a_list = ret_res.get("articles", [])
                match = rank_knowledge_matches(q, k_list, a_list)
                if match:
                    matched_content, matched_title = match
        except Exception as err:
            print(f"Error in test-match endpoint: {err}")
            
    if not matched_content:
        # Local JSON fallback
        q_words = [word.strip("?,.!") for word in q.lower().split()]
        for article in store_articles:
            keywords = article.get("keywords", [])
            for keyword in keywords:
                if keyword in q_words or keyword in q.lower():
                    matched_content = article["content"]
                    matched_title = article["title"]
                    break
            if matched_content:
                break
                
    return {
        "query": q,
        "store_id": store_id,
        "matched_title": matched_title,
        "matched_content": matched_content
    }

@app.get("/api/test-agent")
async def test_agent_endpoint(q: str, store_id: str = "hoverboard_store"):
    # 1. Detect intent and risk
    from app.services.support_brain import detect_intent_and_risk, generate_support_reply
    intent, risk_level, should_escalate, escalation_reason = detect_intent_and_risk(q)
    
    # 2. Retrieve knowledge matching same logic as chat_endpoint
    store_articles = knowledge_base.get(store_id, [])
    matched_content = None
    matched_title = None
    
    if supabase_client:
        try:
            from app.services.knowledge_service import KnowledgeService
            ret_res = await KnowledgeService.get_support_knowledge(
                query=q,
                store_id=store_id
            )
            if ret_res.get("success"):
                k_list = ret_res.get("knowledge", [])
                a_list = ret_res.get("articles", [])
                match = rank_knowledge_matches(q, k_list, a_list)
                if match:
                    matched_content, matched_title = match
        except Exception as err:
            print(f"Error in test-agent knowledge search: {err}")
            
    if not matched_content:
        # Local JSON fallback
        q_words = [word.strip("?,.!") for word in q.lower().split()]
        for article in store_articles:
            keywords = article.get("keywords", [])
            for keyword in keywords:
                if keyword in q_words or keyword in q.lower():
                    matched_content = article["content"]
                    matched_title = article["title"]
                    break
            if matched_content:
                break
                
    # 3. Call generate_support_reply to see the mock or real answer
    brain_res = generate_support_reply(
        store_id=store_id,
        session_id="test-session-agent",
        user_message=q,
        previous_context=[],
        retrieved_knowledge=matched_content,
        rules_fallback_reply="General support rules fallback answer.",
        matched_title=matched_title
    )
    
    route_decision = "escalated" if brain_res["should_escalate"] else (
        "answered_by_minimax" if brain_res["brain_mode"] == "minimax" else "rules_fallback"
    )
    
    return {
        "query": q,
        "store_id": store_id,
        "detected_intent": brain_res["intent"],
        "risk_level": risk_level,
        "route_decision": route_decision,
        "matched_titles": [matched_title] if matched_title else [],
        "brain_mode": brain_res["brain_mode"],
        "final_answer_preview": brain_res["reply_text"]
    }
def rank_knowledge_matches(query_text: str, knowledge_list: list, articles_list: list):
    query_words = set(w.strip("?,.!") for w in query_text.lower().split() if len(w) > 3)
    best_match = None
    best_score = 0
    
    # 1. Rank product_knowledge entries
    for item in knowledge_list:
        title = item.get("title", "").lower()
        content = item.get("content", "").lower()
        
        # Calculate overlap score
        score = sum(1 for w in query_words if w in title) * 3 + sum(1 for w in query_words if w in content)
        
        # Prioritize kids/beginner keywords for 6.5 inch hoverboard
        if "9" in query_text or "kids" in query_text.lower() or "child" in query_text.lower() or "beginner" in query_text.lower():
            if "6.5" in title or "6.5" in content or "beginner" in title:
                score += 5
                
        if score > best_score:
            best_score = score
            best_match = (item.get("content"), item.get("title"))
            
    # 2. Rank support_articles entries
    for item in articles_list:
        title = item.get("title", "").lower()
        content = item.get("content", "").lower()
        
        # Calculate overlap score
        score = sum(1 for w in query_words if w in title) * 3 + sum(1 for w in query_words if w in content)
        
        if score > best_score:
            best_score = score
            best_match = (item.get("content"), item.get("title"))
            
    return best_match

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    store_id = request.store_id or request.storeId
    if not store_id:
        raise HTTPException(
            status_code=400,
            detail="Missing store_id or storeId parameter."
        )
    conversation_id = request.conversation_id or request.session_id or request.sessionId
    if not conversation_id:
        raise HTTPException(
            status_code=400,
            detail="Missing conversation_id, session_id, or sessionId parameter."
        )
    message_text = request.message.strip().lower()

    # 1. Validate Store ID
    if store_id not in knowledge_base:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid store_id: '{store_id}'. Must be one of: {list(knowledge_base.keys())}"
        )

    store_articles = knowledge_base[store_id]
    matched_content = None
    matched_title = None

    # 1.5. Check if session is already escalated or in progress
    is_escalated = False
    db_status = "new"
    if supabase_client:
        try:
            log_res = supabase_client.table("chat_logs")\
                .select("status, escalated")\
                .eq("session_id", conversation_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            if log_res.data:
                db_status = log_res.data[0].get("status")
                db_escalated = log_res.data[0].get("escalated", False)
                if db_status in ["needs_escalation", "in_progress"] or db_escalated:
                    is_escalated = True
        except Exception as err:
            print(f"Error checking session escalation status: {err}")

    # Default variables
    brain_mode = "rules"
    intent = "unknown"
    confidence = 0.0
    escalation_reason = ""
    source_used = matched_title
    
    if is_escalated:
        reply = "Our support team has been notified and a representative will reply here shortly."
        source_used = "Staff Takeover Active (Waiting for support representative)"
    else:
        # Check standard chat flow using Support Brain
        # 1. Simple Keyword Match in Supabase DB first, then local JSON
        matched_content = None
        matched_title = None
        
        if supabase_client:
            try:
                from app.services.knowledge_service import KnowledgeService
                ret_res = await KnowledgeService.get_support_knowledge(
                    query=request.message,
                    store_id=store_id
                )
                if ret_res.get("success"):
                    k_list = ret_res.get("knowledge", [])
                    a_list = ret_res.get("articles", [])
                    match = rank_knowledge_matches(request.message, k_list, a_list)
                    if match:
                        matched_content, matched_title = match
            except Exception as db_kb_err:
                print(f"Error searching Supabase knowledge: {db_kb_err}")
                
        # Local JSON fallback matching
        if not matched_content:
            message_words = [word.strip("?,.!") for word in message_text.split()]
            for article in store_articles:
                keywords = article.get("keywords", [])
                for keyword in keywords:
                    if keyword in message_words or keyword in message_text:
                        matched_content = article["content"]
                        matched_title = article["title"]
                        break
                if matched_content:
                    break
                
        # Fallback message
        store_names = {
            "hoverboard_store": "Hoverboard Store UK",
            "hcs_gadgets": "HCS Gadgets Support",
            "aroma_haven": "Aroma Haven Botanicals"
        }
        store_name = store_names.get(store_id, "our store")
        rules_fallback_reply = (
            f"Thank you for contacting {store_name}. I want to make sure you get correct assistance. "
            f"For general guidelines, please make sure your device is charged and operate it only on private land. "
            f"If you need help with a specific order, technical fault, or warranty claim, please email us at contact@hoverboardstore.co.uk "
            f"and our support team will get back to you shortly."
        )
        
        # 2. Fetch history
        previous_context = []
        if supabase_client:
            try:
                logs_res = supabase_client.table("chat_logs")\
                    .select("user_message, assistant_message")\
                    .eq("session_id", conversation_id)\
                    .order("created_at", desc=True)\
                    .limit(3)\
                    .execute()
                if logs_res.data:
                    for log in reversed(logs_res.data):
                        previous_context.append({"sender": "user", "content": log.get("user_message", "")})
                        previous_context.append({"sender": "bot", "content": log.get("assistant_message", "")})
            except Exception as e:
                print(f"Error fetching historical context for brain: {e}")
                
        # 3. Call Support Brain safely
        try:
            from app.services.support_brain import generate_support_reply
            brain_result = generate_support_reply(
                store_id=store_id,
                session_id=conversation_id,
                user_message=request.message,
                previous_context=previous_context,
                retrieved_knowledge=matched_content,
                rules_fallback_reply=rules_fallback_reply,
                matched_title=matched_title
            )
            
            reply = brain_result["reply_text"]
            is_escalated = brain_result["should_escalate"]
            intent = brain_result["intent"]
            confidence = brain_result["confidence"]
            escalation_reason = brain_result["escalation_reason"]
            brain_mode = brain_result["brain_mode"]
            source_used = brain_result["source_used"]
        except Exception as brain_err:
            print(f"ERROR: Support Brain crashed: {brain_err}")
            # Safe absolute fallback
            reply = matched_content if matched_content else rules_fallback_reply
            is_escalated = matched_content is None
            intent = "unknown"
            confidence = 1.0 if matched_content else 0.0
            escalation_reason = f"Support Brain exception: {str(brain_err)}"
            brain_mode = "fallback"
            source_used = matched_title

    # 4. Save to Supabase Chat Logs (if client is active)
    if supabase_client:
        try:
            if is_escalated:
                escalated = True
                status = db_status if db_status == "in_progress" else "needs_escalation"
            else:
                escalated = False
                status = "new"
                
            # Serialize metadata into matched_source safely
            try:
                import json
                safe_source = (source_used[:80] + "...") if source_used and len(source_used) > 80 else source_used
                safe_reason = (escalation_reason[:80] + "...") if escalation_reason and len(escalation_reason) > 80 else escalation_reason
                
                meta_payload = {
                    "brain_mode": brain_mode,
                    "intent": intent,
                    "source": safe_source,
                    "confidence": confidence,
                    "escalation_reason": safe_reason
                }
                matched_source_str = json.dumps(meta_payload)
                if len(matched_source_str) > 255:
                    meta_payload["source"] = safe_source[:40] if safe_source else None
                    meta_payload["escalation_reason"] = safe_reason[:40] if safe_reason else None
                    matched_source_str = json.dumps(meta_payload)
            except Exception as ser_err:
                print(f"ERROR: Failed to serialize metadata: {ser_err}")
                matched_source_str = source_used
            
            log_entry = {
                "store_id": store_id,
                "session_id": conversation_id,
                "user_message": request.message,
                "assistant_message": reply,
                "matched_source": matched_source_str,
                "confidence": confidence,
                "escalated": escalated,
                "status": status
            }
            supabase_client.table("chat_logs").insert(log_entry).execute()
        except Exception as db_err:
            print(f"ERROR: Failed to save conversation log to Supabase: {db_err}")

    return ChatResponse(
        reply=reply,
        conversation_id=conversation_id,
        store_id=store_id,
        matched_article=source_used
    )

@app.get("/api/conversations", dependencies=[Depends(verify_admin_token)])
async def get_conversations(store_id: Optional[str] = None):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your backend/.env file."
        )
    try:
        query = supabase_client.table("chat_logs").select("*").order("created_at", desc=True)
        if store_id:
            query = query.eq("store_id", store_id)
        logs_res = query.execute()
        
        logs = logs_res.data or []
        for log in logs:
            if log.get("matched_source") == "__archived__":
                log["status"] = "archived"
                
            raw_source = log.get("matched_source")
            log["brain_mode"] = "rules"
            log["intent"] = "unknown"
            log["escalation_reason"] = ""
            
            if raw_source:
                try:
                    import json
                    meta = json.loads(raw_source)
                    if isinstance(meta, dict) and "brain_mode" in meta:
                        log["brain_mode"] = meta.get("brain_mode", "rules")
                        log["intent"] = meta.get("intent", "unknown")
                        log["matched_source"] = meta.get("source")
                        log["confidence"] = meta.get("confidence", log.get("confidence", 0.0))
                        log["escalation_reason"] = meta.get("escalation_reason", "")
                except json.JSONDecodeError:
                    pass

        # Fetch all agent replies
        replies_res = supabase_client.table("agent_replies").select("*").order("created_at", desc=True).execute()
        replies = replies_res.data or []
        for r in replies:
            r["role"] = "support_agent"
            r["message_type"] = "agent_reply"

        return {
            "logs": logs,
            "agent_replies": replies
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query conversation data: {str(e)}"
        )

@app.put("/api/conversations/{session_id}/status", dependencies=[Depends(verify_admin_token)])
async def update_conversation_status(session_id: str, status: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your backend/.env file."
        )
    
    allowed_statuses = {"new", "needs_escalation", "in_progress", "resolved", "archived"}
    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: '{status}'. Must be one of: {list(allowed_statuses)}"
        )
        
    try:
        # Get existing logs to check if it was previously archived
        existing_res = supabase_client.table("chat_logs")\
            .select("matched_source")\
            .eq("session_id", session_id)\
            .execute()
        existing_logs = existing_res.data or []
        was_archived = any(log.get("matched_source") == "__archived__" for log in existing_logs)
        
        # Bypassing DB check constraint by mapping "archived" -> "resolved" with metadata tag
        db_status = "resolved" if status == "archived" else status
        escalated = (status == "needs_escalation")
        
        update_payload = {"status": db_status, "escalated": escalated}
        if status == "archived":
            update_payload["matched_source"] = "__archived__"
        elif was_archived:
            update_payload["matched_source"] = None
            
        response = supabase_client.table("chat_logs")\
            .update(update_payload)\
            .eq("session_id", session_id)\
            .execute()
            
        return {
            "status": "success",
            "message": f"Updated conversation {session_id} to status {status}",
            "updated_count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update conversation status: {str(e)}"
        )

@app.delete("/api/conversations/{session_id}", dependencies=[Depends(verify_admin_token)])
async def delete_conversation(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        # 1. Delete child tables by session_id directly
        child_tables = ["reply_drafts", "staff_notes", "agent_replies"]
        for table in child_tables:
            try:
                supabase_client.table(table).delete().eq("session_id", session_id).execute()
            except Exception as e:
                print(f"Skipping direct delete by session_id for {table}: {e}")
                
        # 2. Handle conversations/messages legacy/parallel table cascade
        try:
            conv_res = supabase_client.table("conversations").select("id").eq("session_id", session_id).execute()
            if conv_res.data:
                for conv in conv_res.data:
                    conv_uuid = conv.get("id")
                    # Clean staff_notes referencing conversation_id if foreign keys require it
                    try:
                        supabase_client.table("staff_notes").delete().eq("conversation_id", conv_uuid).execute()
                    except Exception as err:
                        print(f"Skipping staff_notes delete by conversation_id: {err}")
                    # Delete conversations parent (will cascade to messages and escalations tables)
                    supabase_client.table("conversations").delete().eq("id", conv_uuid).execute()
        except Exception as e:
            print(f"Skipping conversations table cascade check: {e}")
            
        # 3. Delete parent chat logs
        supabase_client.table("chat_logs").delete().eq("session_id", session_id).execute()
        
        return {
            "status": "success",
            "message": f"Successfully deleted conversation {session_id} and all related records."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete conversation: {str(e)}"
        )

@app.get("/api/notes/{session_id}", dependencies=[Depends(verify_admin_token)])
async def get_notes(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        response = supabase_client.table("staff_notes")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at", desc=False)\
            .execute()
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch staff notes: {str(e)}"
        )

@app.post("/api/notes", dependencies=[Depends(verify_admin_token)])
async def create_note(request: NoteRequest):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        note_entry = {
            "session_id": request.session_id,
            "note": request.note,
            "author": request.author
        }
        response = supabase_client.table("staff_notes").insert(note_entry).execute()
        return response.data[0] if response.data else {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save staff note: {str(e)}"
        )

@app.get("/api/draft/{session_id}", dependencies=[Depends(verify_admin_token)])
async def get_draft(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        response = supabase_client.table("reply_drafts")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        if response.data:
            return response.data[0]
        return {"session_id": session_id, "draft_text": ""}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch reply draft: {str(e)}"
        )

@app.post("/api/draft", dependencies=[Depends(verify_admin_token)])
async def save_draft(request: DraftRequest):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        draft_entry = {
            "session_id": request.session_id,
            "draft_text": request.draft_text
        }
        response = supabase_client.table("reply_drafts")\
            .upsert(draft_entry)\
            .execute()
        return response.data[0] if response.data else {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save reply draft: {str(e)}"
        )

@app.delete("/api/draft/{session_id}", dependencies=[Depends(verify_admin_token)])
async def delete_draft(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        response = supabase_client.table("reply_drafts")\
            .delete()\
            .eq("session_id", session_id)\
            .execute()
        return {"status": "success", "deleted_count": len(response.data)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete reply draft: {str(e)}"
        )

@app.get("/api/reply-draft/{session_id}", dependencies=[Depends(verify_admin_token)])
async def get_reply_draft(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        response = supabase_client.table("reply_drafts")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        if response.data:
            return response.data[0]
        return {"session_id": session_id, "draft_text": ""}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch reply draft: {str(e)}"
        )

@app.post("/api/reply-draft", dependencies=[Depends(verify_admin_token)])
async def save_reply_draft(request: ReplyDraftRequest):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        draft_entry = {
            "session_id": request.session_id,
            "draft_text": request.draft_text
        }
        response = supabase_client.table("reply_drafts")\
            .upsert(draft_entry, on_conflict="session_id")\
            .execute()
        return response.data[0] if response.data else {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save reply draft: {str(e)}"
        )

@app.delete("/api/reply-draft/{session_id}", dependencies=[Depends(verify_admin_token)])
async def delete_reply_draft(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        response = supabase_client.table("reply_drafts")\
            .delete()\
            .eq("session_id", session_id)\
            .execute()
        return {"status": "success", "deleted_count": len(response.data)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete reply draft: {str(e)}"
        )

@app.post("/api/agent-replies", dependencies=[Depends(verify_admin_token)])
async def create_agent_reply(request: AgentReplyRequest):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        reply_entry = {
            "session_id": request.session_id,
            "message": request.message,
            "status": "sent"
        }
        response = supabase_client.table("agent_replies").insert(reply_entry).execute()
        return response.data[0] if response.data else {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save agent reply: {str(e)}"
        )

@app.get("/api/agent-replies/{session_id}")
async def get_agent_replies(session_id: str):
    if not supabase_client:
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured."
        )
    try:
        response = supabase_client.table("agent_replies")\
            .select("*")\
            .eq("session_id", session_id)\
            .eq("status", "sent")\
            .order("created_at", desc=False)\
            .execute()
        replies = response.data or []
        for reply in replies:
            reply["role"] = "support_agent"
            reply["message_type"] = "agent_reply"
        return replies
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agent replies: {str(e)}"
        )

@app.get("/api/amazon/health", dependencies=[Depends(verify_admin_token)])
async def get_amazon_health():
    try:
        from app.amazon_client import get_amazon_config_status
        return get_amazon_config_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Amazon health status: {str(e)}"
        )

@app.get("/api/amazon/token-test", dependencies=[Depends(verify_admin_token)])
async def test_amazon_token():
    try:
        from app.amazon_client import get_lwa_access_token, get_amazon_config_status
        config_status = get_amazon_config_status()
        if not config_status["configured"]:
            return {
                "configured": False,
                "token_exchange": "skipped",
                "access_token_received": False,
                "mode": "sandbox_token_test",
                "error": "Connector not configured"
            }
        
        result = await get_lwa_access_token()
        if result.get("success"):
            return {
                "configured": True,
                "token_exchange": "success",
                "access_token_received": True,
                "expires_in": result.get("expires_in"),
                "mode": "sandbox_token_test"
            }
        else:
            return {
                "configured": True,
                "token_exchange": "failed",
                "access_token_received": False,
                "mode": "sandbox_token_test",
                "error": result.get("error")
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token test invocation failed: {str(e)}"
        )

@app.get("/api/amazon/sandbox/marketplaces", dependencies=[Depends(verify_admin_token)])
async def get_sandbox_marketplaces_route():
    try:
        from app.amazon_client import get_sandbox_marketplaces, get_amazon_config_status
        config_status = get_amazon_config_status()
        if not config_status["configured"]:
            return {
                "configured": False,
                "token_exchange": "skipped",
                "sp_api_call": "skipped",
                "endpoint": "sellers marketplace participations",
                "mode": "sandbox_marketplace_test",
                "error": "Connector not configured"
            }
        
        result = await get_sandbox_marketplaces()
        if result.get("success"):
            return {
                "configured": True,
                "token_exchange": "success",
                "sp_api_call": "success",
                "endpoint": "sellers marketplace participations",
                "marketplace_count": result.get("marketplace_count"),
                "marketplaces": result.get("marketplaces"),
                "mode": "sandbox_marketplace_test"
            }
        else:
            return {
                "configured": True,
                "token_exchange": result.get("token_exchange", "success"),
                "sp_api_call": "failed",
                "endpoint": "sellers marketplace participations",
                "mode": "sandbox_marketplace_test",
                "error": result.get("error")
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sandbox marketplaces test invocation failed: {str(e)}"
        )


@app.get("/api/amazon/sandbox/orders", dependencies=[Depends(verify_admin_token)])
async def get_sandbox_orders_route(marketplace_ids: str = None, created_after: str = None):
    try:
        from app.amazon_client import get_sandbox_orders, get_amazon_config_status
        config_status = get_amazon_config_status()
        if not config_status["configured"]:
            return {
                "configured": False,
                "token_exchange": "skipped",
                "sp_api_call": "skipped",
                "endpoint": "orders list",
                "order_count": 0,
                "orders": [],
                "mode": "sandbox_orders_test",
                "error": "Connector not configured"
            }
            
        m_list = [m.strip() for m in marketplace_ids.split(",")] if marketplace_ids else None
        
        result = await get_sandbox_orders(marketplace_ids=m_list, created_after=created_after)
        if result.get("success"):
            return {
                "configured": True,
                "token_exchange": "success",
                "sp_api_call": "success",
                "endpoint": "orders list",
                "order_count": result.get("order_count"),
                "orders": result.get("orders"),
                "mode": "sandbox_orders_test"
            }
        else:
            return {
                "configured": True,
                "token_exchange": result.get("token_exchange", "success"),
                "sp_api_call": "failed",
                "endpoint": "orders list",
                "order_count": 0,
                "orders": [],
                "mode": "sandbox_orders_test",
                "error": result.get("error")
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sandbox orders test invocation failed: {str(e)}"
        )


@app.get("/api/amazon/orders/{order_id}", dependencies=[Depends(verify_admin_token)])
async def get_sandbox_order_lookup_route(order_id: str):
    try:
        from app.amazon_client import get_sandbox_order, get_amazon_config_status
        config_status = get_amazon_config_status()
        if not config_status["configured"]:
            return {
                "configured": False,
                "token_exchange": "skipped",
                "sp_api_call": "skipped",
                "endpoint": "order lookup",
                "order": None,
                "mode": "sandbox_order_lookup",
                "error": "Connector not configured"
            }
            
        result = await get_sandbox_order(order_id)
        if result.get("success"):
            return {
                "configured": True,
                "token_exchange": "success",
                "sp_api_call": "success",
                "endpoint": "order lookup",
                "order": result.get("order"),
                "mode": "sandbox_order_lookup"
            }
        else:
            return {
                "configured": True,
                "token_exchange": result.get("token_exchange", "success"),
                "sp_api_call": "failed",
                "endpoint": "order lookup",
                "order": None,
                "mode": "sandbox_order_lookup",
                "error": result.get("error")
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sandbox order lookup invocation failed: {str(e)}"
        )





@app.post("/api/amazon/draft/analyse", response_model=AmazonAnalysisResponse, dependencies=[Depends(verify_admin_token)])
async def analyse_amazon_draft_route(request: AmazonAnalysisRequest):
    import re
    from app.amazon_client import get_sandbox_order
    from app.services.knowledge_service import KnowledgeService

    message_lower = request.message.lower()
    
    # 1. Resolve store_id and channel
    store_id = None
    channel = "shopify"  # Default fallback
    
    if request.session_id and supabase_client:
        try:
            log_res = supabase_client.table("chat_logs").select("store_id").eq("session_id", request.session_id).limit(1).execute()
            if log_res.data:
                store_id = log_res.data[0].get("store_id")
                store_res = supabase_client.table("stores").select("channel").eq("id", store_id).limit(1).execute()
                if store_res.data:
                    channel = store_res.data[0].get("channel")
                else:
                    if "amazon" in store_id.lower() or "gift" in store_id.lower():
                        channel = "amazon"
        except Exception as e:
            print(f"Error resolving channel/store for session {request.session_id}: {e}")
            
    if request.order_id:
        channel = "amazon"

    # 2. Query KnowledgeService Cache
    knowledge_res = await KnowledgeService.get_support_knowledge(
        query=request.message,
        channel=channel,
        store_id=store_id
    )
    
    knowledge_found = False
    knowledge_sources = []
    retrieved_context_summary = None
    human_review_required_from_knowledge = False
    suggested_reply = None
    
    category = "unknown"
    risk = "low"
    action = "draft_reply"

    if knowledge_res.get("success"):
        knowledge_found = True
        articles = knowledge_res.get("articles", [])
        knowledge_entries = knowledge_res.get("knowledge", [])
        
        sources_set = set()
        summary_parts = []
        
        matched_guide_type = None
        guide_content = None
        
        for pk_entry in knowledge_entries:
            if pk_entry.get("title"):
                sources_set.add(pk_entry["title"])
            if pk_entry.get("risk_level") == "high" or pk_entry.get("human_review_required"):
                human_review_required_from_knowledge = True
            
            if pk_entry.get("knowledge_type") in ["reset_guide", "battery", "charging"]:
                matched_guide_type = pk_entry.get("knowledge_type")
                guide_content = pk_entry.get("content")
                
            summary_parts.append(f"[{pk_entry.get('title')}]: {pk_entry.get('content')}")
            
        for art in articles:
            if art.get("title"):
                sources_set.add(art["title"])
            summary_parts.append(f"[{art.get('title')}]: {art.get('content')}")
            
        knowledge_sources = list(sources_set)
        retrieved_context_summary = " | ".join(summary_parts) if summary_parts else None

        # Build custom suggested reply based on retrieved knowledge
        if human_review_required_from_knowledge:
            category = "battery_or_safety_issue"
            risk = "high"
            action = "escalate"
            content_to_use = guide_content or "Charge your hoverboard only on a flat, non-flammable surface..."
            suggested_reply = (
                f"Dear buyer, we have received your urgent message regarding your hoverboard. "
                f"Please be assured that we take safety issues very seriously. "
                f"Guideline: {content_to_use} "
                f"This ticket has been escalated directly to our support team for immediate human review. Please stop using the product."
            )
        elif matched_guide_type == "charging":
            category = "faulty_product"
            risk = "medium"
            action = "draft_reply"
            content_to_use = guide_content or "If the hoverboard is not charging..."
            suggested_reply = (
                f"Dear buyer, thank you for contacting us regarding your hoverboard. "
                f"Here are the troubleshooting steps: {content_to_use}"
            )
        elif matched_guide_type == "reset_guide":
            category = "faulty_product"
            risk = "medium"
            action = "draft_reply"
            content_to_use = guide_content or "Follow these steps to calibrate the hoverboard..."
            suggested_reply = (
                f"Dear buyer, thank you for contacting us regarding your hoverboard. "
                f"Here is the reset and calibration guide: {content_to_use}"
            )
        else:
            category = "general_inquiry"
            risk = "low"
            action = "draft_reply"
            if articles:
                suggested_reply = f"Dear buyer, thank you for your query. Regarding your request: {articles[0].get('content')}"
            else:
                suggested_reply = "Dear buyer, thank you for contacting us. We are reviewing your request based on our support guides and will update you shortly."

    else:
        # Fallback to existing keyword classification rules
        # Battery / fire safety concern (High Risk / Escalate)
        safety_keywords = ["battery", "fire", "smoke", "smell", "odor", "hot", "heating", "overheating", "overheat", "burn", "charge", "charging", "explode", "explosion", "hazard", "safety", "spark", "unsafe", "dangerous", "shock"]
        if any(k in message_lower for k in safety_keywords):
            category = "battery_or_safety_issue"
            risk = "high"
            action = "escalate"
        
        # Negative feedback threat
        elif any(k in message_lower for k in ["feedback", "review", "1 star", "one star", "negative feedback", "report to amazon", "threat", "bad review"]):
            category = "negative_feedback_threat"
            risk = "high"
            action = "escalate"
            
        # A-to-Z Claim
        elif any(k in message_lower for k in ["a-to-z", "claim", "open claim", "guarantee claim", "dispute"]):
            category = "a_to_z_claim_risk"
            risk = "high"
            action = "escalate"
            
        # Check Angry Customer
        elif any(k in message_lower for k in ["angry", "furious", "scam", "cheat", "terrible", "worst", "fraud", "lawyer", "legal", "sue"]):
            category = "angry_customer"
            risk = "high"
            action = "escalate"
            
        # Wrong item
        elif any(k in message_lower for k in ["wrong", "different", "not what i ordered"]):
            category = "wrong_item_received"
            risk = "medium"
            action = "draft_reply"
            
        # Damaged / physical damage (High Risk / Escalate)
        elif any(k in message_lower for k in ["damaged", "cracked", "scratched", "broken", "smashed", "shattered"]):
            category = "damaged_item"
            risk = "high"
            action = "escalate"
            
        # Return request
        elif any(k in message_lower for k in ["return", "send back", "label"]):
            category = "return_request"
            risk = "medium"
            action = "draft_reply"
            
        # Cancellation
        elif any(k in message_lower for k in ["cancel", "cancellation", "stop order", "dont send"]):
            category = "cancellation_request"
            risk = "low"
            action = "draft_reply"
            
        # Refund
        elif any(k in message_lower for k in ["refund", "money back"]):
            category = "refund_question"
            risk = "high"
            action = "escalate"
            
        # Warranty
        elif any(k in message_lower for k in ["warranty", "guarantee"]):
            category = "warranty_question"
            risk = "high"
            action = "escalate"
            
        # Invoice
        elif any(k in message_lower for k in ["invoice", "vat", "receipt", "bill"]):
            category = "invoice_request"
            risk = "low"
            action = "draft_reply"
            
        # Delivery status / Item not received
        elif any(k in message_lower for k in ["where", "tracking", "status", "lost", "not arrived", "delivery", "delivered", "package"]):
            if any(k in message_lower for k in ["lost", "not arrived", "never arrived", "not received"]):
                category = "item_not_received"
                risk = "medium"
                action = "human_review"
            else:
                category = "delivery_status"
                risk = "low"
                action = "draft_reply"
                
        # Faulty Product (Medium Risk / Draft Reply)
        elif any(k in message_lower for k in ["faulty", "defective", "malfunction", "not working", "calibrate", "calibration", "reset", "beeping", "beep"]):
            category = "faulty_product"
            risk = "medium"
            action = "draft_reply"

        # Extract Order ID if not explicitly provided
        order_id = request.order_id
        if not order_id:
            match = re.search(r"\b\d{3}-\d{7}-\d{7}\b", request.message)
            if match:
                order_id = match.group(0)

        # Dynamic suggested reply template generation
        order_status = None
        fulfillment_channel = None

        if order_id:
            try:
                lookup_result = await get_sandbox_order(order_id)
                if lookup_result.get("success") and lookup_result.get("order"):
                    order_status = lookup_result["order"].get("order_status")
                    fulfillment_channel = lookup_result["order"].get("fulfillment_channel")
            except Exception as e:
                print(f"Error querying sandbox order {order_id} in draft analysis: {e}")

        # Generate custom message drafts based on classification category and order status
        if action == "escalate":
            suggested_reply = (
                f"Dear buyer, we have received your urgent message regarding Amazon Order {order_id if order_id else '[Order ID]'}. "
                f"Please be assured that we take safety and safety issues very seriously. This ticket has been escalated "
                f"directly to our senior management team for immediate investigation. A specialist will review your details "
                f"and follow up on this thread shortly. Thank you for your patience."
            )
        elif category == "cancellation_request":
            if order_status == "Shipped":
                suggested_reply = (
                    f"Dear buyer, thank you for your cancellation request. We checked the status of Order {order_id}. "
                    f"However, this package has already been shipped and is currently in transit (Fulfillment: {fulfillment_channel}). "
                    f"As it cannot be cancelled at this stage, you are welcome to refuse the delivery or return the item "
                    f"once it arrives to receive a full refund. Thank you."
                )
            elif order_status == "Unshipped":
                suggested_reply = (
                    f"Dear buyer, thank you for your request. We have verified that Order {order_id} is currently 'Unshipped'. "
                    f"We have successfully cancelled your order as requested. You will receive a refund confirmation from Amazon shortly."
                )
            else:
                suggested_reply = (
                    f"Dear buyer, thank you for your cancellation request. To help us process this cancellation, could you please "
                    f"reply with your Amazon Order ID? Once received, we will verify the shipment status immediately. Thank you."
                )
        elif category in ["delivery_status", "item_not_received"]:
            if order_status == "Shipped":
                suggested_reply = (
                    f"Dear buyer, thank you for your message regarding the delivery status of Order {order_id}. "
                    f"Our records show that your order has been successfully shipped (Fulfillment: {fulfillment_channel}) "
                    f"and is currently in transit. You can view real-time tracking information inside your Amazon buyer portal. "
                    f"Please let us know if there is anything else we can do to assist you."
                )
            elif order_status == "Unshipped":
                suggested_reply = (
                    f"Dear buyer, thank you for your message regarding the status of Order {order_id}. "
                    f"Your order is currently 'Unshipped' and is being prepared for dispatch. We will provide tracking information "
                    f"as soon as it leaves our warehouse. Thank you for your patience."
                )
            else:
                suggested_reply = (
                    f"Dear buyer, thank you for contacting us regarding delivery. Could you please provide your Amazon Order ID? "
                    f"This will allow us to check the shipping status and coordinate with the carrier. Thank you."
                )
        elif category == "invoice_request":
            suggested_reply = (
                f"Dear buyer, thank you for your request. We have generated the VAT invoice for Order {order_id if order_id else '[Order ID]'}. "
                f"You can download your document directly from your Amazon account order history under the 'Invoice' dropdown. "
                f"Please let us know if you have any trouble finding it. Thank you."
            )
        elif category == "wrong_item_received":
            suggested_reply = (
                f"Dear buyer, we apologize for sending the wrong item. We want to resolve this for you as quickly as possible. "
                f"Could you please initiate a wrong-item return request inside your Amazon account page for Order {order_id if order_id else '[Order ID]'}? "
                f"Once initiated, we will process a replacement shipment or a full refund. Thank you for your patience."
            )
        elif category == "return_request":
            suggested_reply = (
                f"Dear buyer, thank you for your return request. To return your item, please open your Amazon order details page "
                f"for Order {order_id if order_id else '[Order ID]'} and click 'Return or replace items'. You will receive a policy-compliant "
                f"return label to drop off the package. Thank you."
            )
        elif category == "faulty_product":
            if any(w in message_lower for w in ["hoverboard", "scooter", "board", "segway", "wheel"]):
                suggested_reply = (
                    f"Dear buyer, thank you for your query regarding your hoverboard. Most calibration or beeping faults can be "
                    f"resolved by resetting the board: place it on a flat surface, hold the power button down for 10 seconds until the lights flash, "
                    f"then restart. Please let us know if this solves the issue, and we will advise further if needed. Thank you."
                )
            else:
                suggested_reply = (
                    "Thank you for your message. We’re sorry to hear you’re experiencing an issue with the product. "
                    "Our support team will review your order and the fault details. Please avoid further use if you believe "
                    "the product may be unsafe, and we will advise the next step shortly."
                )
        else:
            suggested_reply = (
                f"Dear buyer, thank you for your message. We have received your inquiry. To help us assist you, could you please "
                f"provide your Amazon Order ID and any additional details? Our team is reviewing your message and will respond shortly."
            )

    return AmazonAnalysisResponse(
        session_id=request.session_id,
        issue_category=category,
        risk_level=risk,
        recommended_action=action,
        suggested_reply=suggested_reply,
        knowledge_found=knowledge_found,
        knowledge_sources=knowledge_sources,
        retrieved_context_summary=retrieved_context_summary,
        human_review_required_from_knowledge=human_review_required_from_knowledge
    )


from fastapi.staticfiles import StaticFiles
import os
import logging

logger = logging.getLogger("uvicorn.error")

# Determine the best path for serving frontend static files
# 1. Deployed container path (Railway root = backend): backend/frontend
# 2. Local workspace development path: project-level frontend folder
app_dir = os.path.dirname(__file__)
backend_frontend_dir = os.path.abspath(os.path.join(app_dir, "../frontend"))
project_frontend_dir = os.path.abspath(os.path.join(app_dir, "../../frontend"))

frontend_dir = None
if os.path.exists(backend_frontend_dir) and os.path.isdir(backend_frontend_dir):
    frontend_dir = backend_frontend_dir
    logger.info(f"Serving static frontend from container mirrored path: {frontend_dir}")
elif os.path.exists(project_frontend_dir) and os.path.isdir(project_frontend_dir):
    frontend_dir = project_frontend_dir
    logger.info(f"Serving static frontend from local workspace path: {frontend_dir}")
else:
    logger.warning("Frontend static directory not found. Static files serving is disabled, but API routes remain active.")

if frontend_dir:
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


