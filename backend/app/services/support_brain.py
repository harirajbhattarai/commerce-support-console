import os
import requests
from typing import List, Dict, Optional, Any
from app.config import settings

def detect_intent_and_risk(message_text: str):
    """
    Classifies user message into predefined intents and assigns risk levels.
    Enforces rule-based checks for safety, complaints, and live human transfers.

    Priority order (highest wins):
      1. Safety danger (fire/smoke/sparks/burning/overheating/swelling/smell+device)
      2. Explicit human agent request
      3. Legal threat
      4. Payment/billing issue
      5. Order-specific action (requires account lookup)
      6. Damaged-on-arrival
      7. Explicit refund demand
      8. Complaint / frustration
      9. Standard low-risk intents (handled by chatbot)
    """
    msg = message_text.lower().strip()

    # ── 1. SAFETY DANGER KEYWORDS ─────────────────────────────────────────────
    # Removed in Batch 1: Handled upstream by deterministic hard_safety_gate

    # ── 2. HUMAN TRANSFER INTENT ──────────────────────────────────────────────
    # Removed in Batch 1: Handled upstream by deterministic hard_human_handoff_gate

    # ── 3. LEGAL THREAT ───────────────────────────────────────────────────────
    legal_keywords = [
        "sue", "legal", "lawyer", "court", "ombudsman",
        "trading standards", "solicitor", "legal action",
    ]
    has_legal_threat = any(kw in msg for kw in legal_keywords)

    # ── 4. PAYMENT / BILLING ──────────────────────────────────────────────────
    payment_keywords = [
        "chargeback", "stripe", "paypal", "double charge", "billing",
        "card declined", "payment failed", "checkout error",
    ]
    has_payment_issue = any(kw in msg for kw in payment_keywords)

    # ── 5. ORDER-SPECIFIC ACTIONS (requires account lookup) ───────────────────
    order_actions = [
        "where is my order", "track", "tracking", "order status", "delivery status",
        "haven't received", "parcel status", "when will it arrive", "delivered but not received",
        "cancel my order", "cancel order", "cancellation",
        "change address", "change shipping address",
        "refund approval", "replacement approval", "refund request", "replace my",
    ]
    is_order_specific = any(kw in msg for kw in order_actions)

    # ── INTENT + RISK ASSIGNMENT (priority order) ─────────────────────────────
    intent = "unknown"
    risk_level = "low"

    # Safety and explicit human requests are now handled upstream
    if has_legal_threat:
        intent = "complaint"
        risk_level = "high"
    elif has_payment_issue:
        intent = "unknown"
        risk_level = "high"
    elif is_order_specific:
        intent = "order_issue"
        risk_level = "high"
    elif any(kw in msg for kw in [
        "dead on arrival", "arrived damaged", "arrived broken",
        "damaged on arrival", "box was damaged",
    ]):
        intent = "damaged_on_arrival"
        risk_level = "high"
    elif any(kw in msg for kw in [
        "refund approval", "refund my money", "charge back", "chargeback",
    ]):
        intent = "refund_request"
        risk_level = "high"
    elif any(kw in msg for kw in [
        "angry", "upset", "complaint", "complain", "scam",
        "rip off", "waste of money", "useless", "terrible", "worst",
    ]):
        intent = "complaint"
        risk_level = "high"

    # ── STANDARD LOW-RISK INTENTS (only reached when risk_level is still 'low') ─
    if intent == "unknown":
        if any(kw in msg for kw in [
            "delivery", "shipping", "shipment", "dispatch",
            "how long is delivery", "how long to ship", "postage",
        ]):
            intent = "shipping_times"
        elif any(kw in msg for kw in [
            "return", "returns", "exchange", "refund policy", "return policy",
        ]):
            intent = "return_policy"
        elif any(kw in msg for kw in ["battery", "charge", "charger", "overcharge"]):
            if "safety" in msg or "safe" in msg:
                intent = "battery_safety"
            else:
                intent = "charging_problem"
        elif any(kw in msg for kw in [
            "reset", "calibrate", "calibration", "beeping", "flash", "flashing", "red light",
        ]):
            intent = "reset_help"
        elif any(kw in msg for kw in [
            "year old", "age", "suitable", "kids", "children", "years old",
        ]):
            intent = "age_suitability"
        elif any(kw in msg for kw in [
            "recommendation", "recommend", "best", "which", "buy", "suggest",
        ]):
            intent = "product_recommendation"
        elif any(kw in msg for kw in [
            "discount", "coupon", "code", "promo", "voucher", "deal", "signup",
        ]):
            intent = "discount_question"
        elif any(kw in msg for kw in ["warranty", "guarantee"]):
            intent = "warranty_question"

    # ── ESCALATION DECISION ───────────────────────────────────────────────────
    if risk_level == "high":
        escalate = True
        escalation_reason = f"High risk query ({intent}) requires support agent review"
    else:
        escalate = False
        escalation_reason = ""

    return intent, risk_level, escalate, escalation_reason

def construct_system_prompt(store_id: str, retrieved_knowledge: str) -> str:
    """
    Creates the system instructions for the LLM.
    """
    store_names = {
        "hoverboard_store": "Hoverboard Store UK",
        "hcs_gadgets": "HCS Gadgets",
        "aroma_haven": "Aroma Haven Botanicals"
    }
    store_name = store_names.get(store_id, "our store")

    general_policies = """
- Product Stopped Working / Not Turning On: If your hoverboard has stopped working, first make sure it is fully charged and check the charger light. Do not use or charge it if there is any burning smell, smoke, overheating, swelling, water damage, or visible damage. If it still does not work, contact contact@hoverboardstore.co.uk with your order number, a short description of the issue, and photos/videos if safe. Our team can then advise the next step under the 12-month warranty where applicable.
- Reset & Calibration: If the hoverboard is beeping or has red flashing lights, it may need to be reset. Turn it off, place it on a flat level surface, hold the power button down for 10 seconds until the lights flash, turn it off again, and then turn it back on.
- Warranty: Hoverboard Store provides a 12-Month Warranty covering manufacturing defects and technical malfunctions. Physical drops, water damage, and general wear and tear are not covered.
- Returns: Customers can return unused items in their original packaging within 30 days. Contact contact@hoverboardstore.co.uk to initiate.
- Contact: For any other support issues, customers should email contact@hoverboardstore.co.uk.
"""

    return f"""You are the friendly customer support assistant for {store_name}.
Your job is to answer customer questions accurately and safely using the provided Knowledge Base context and general policies below.

=== STRICT GUIDELINES ===
1. Only answer based on the official Knowledge Base context and general policies provided. If a question is not covered at all, ask the customer to contact contact@hoverboardstore.co.uk for human help.
2. DO NOT invent, hallucinate, or assume any customer order details, tracking numbers, shipping dates, or postcodes.
3. DO NOT promise, guarantee, or authorize refunds, replacements, or discount codes unless they are explicitly written in the context.
4. DO NOT make any legal assertions or medical claims.
5. If the customer reports any safety hazards, battery swelling, overheating, sparks, smoke, fire, or burning smells, instruct them to stop using and unplug the device immediately, place it in a safe outdoor location, and escalate to a human agent. Do not attempt any other troubleshooting.
6. Keep your answers brief, friendly, helpful, and under 3-4 sentences where possible.

=== GENERAL POLICIES ===
{general_policies}

=== KNOWLEDGE BASE CONTEXT ===
{retrieved_knowledge}
"""

def generate_support_reply(
    store_id: str,
    session_id: str,
    user_message: str,
    previous_context: Optional[List[Dict[str, str]]] = None,
    retrieved_knowledge: Optional[str] = None,
    rules_fallback_reply: str = "",
    matched_title: Optional[str] = None,
    semantic_understanding: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Orchestrates intent detection, safety routing, and response generation (MiniMax or Fallback).
    """
    # 1. Detect Intent and Safety check
    if semantic_understanding and semantic_understanding.intent != "unknown" and semantic_understanding.intent != "unknown_general":
        intent = semantic_understanding.intent.value if hasattr(semantic_understanding.intent, "value") else str(semantic_understanding.intent)
        risk_level = semantic_understanding.risk_level.value if hasattr(semantic_understanding.risk_level, "value") else str(semantic_understanding.risk_level)
        should_escalate = False
        escalation_reason = ""
        if risk_level == "high":
            should_escalate = True
            escalation_reason = f"High risk query ({intent}) requires support agent review (Semantic)"
    else:
        intent, risk_level, should_escalate, escalation_reason = detect_intent_and_risk(user_message)
    msg = user_message.lower().strip()

    # 2. If safety router triggers forced escalation, return holding reply immediately
    if should_escalate:
        if intent == "speak_to_human":
            reply_text = "Thanks — I’ve passed this to our support team. A team member will reply here shortly."
        elif intent == "battery_safety":
            reply_text = "Please stop using the hoverboard immediately. Do not charge it again. If it is safe, unplug it and keep it away from flammable materials. Do not attempt to repair the battery or charger yourself. Our support team has been notified and will reply here shortly. You can also contact contact@hoverboardstore.co.uk."
        elif intent == "order_issue":
            reply_text = "To help you with this order request, please provide your order reference number, full name, and billing postcode. Once verified, our support team will update you shortly."
        else:
            reply_text = "Our support team has been notified and a representative will reply here shortly."

        return {
            "reply_text": reply_text,
            "intent": intent,
            "confidence": 0.0,
            "source_used": matched_title or "Safety Router Escalation",
            "should_escalate": True,
            "escalation_reason": escalation_reason,
            "brain_mode": "rules",
            "route_decision": "escalated"
        }

    # 3. Check if MiniMax is configured and available
    api_key = settings.MINIMAX_API_KEY
    model_name = settings.MINIMAX_MODEL

    # If API key is missing OR semantic understanding failed (timeout, network, etc.), fallback to rules
    has_semantic_error = hasattr(semantic_understanding, "error_reason") and semantic_understanding.error_reason is not None

    if not api_key or has_semantic_error:
        # Fallback to rules if API key missing or semantic parsing failed
        if "stops working" in msg or "not working" in msg or "stopped working" in msg:
            reply_text = "Sorry to hear that. If your hoverboard has stopped working, first make sure it is fully charged and check the charger light. Do not use or charge it if there is any burning smell, smoke, overheating, swelling, water damage, or visible damage. If it still does not work, contact contact@hoverboardstore.co.uk with your order number, a short description of the issue, and photos/videos if safe. Our team can then advise the next step under the 12-month warranty where applicable."
        elif "reset" in msg or "calibrate" in msg or "calibration" in msg:
            reply_text = "If your hoverboard is beeping or flashing red lights, it may need a reset. Turn it off, place it on a flat, level surface, press and hold the power button for 10 seconds until the lights flash, turn it off again, and then turn it back on to calibrate it."
        elif "delivery" in msg or "shipping" in msg or "dispatch" in msg or "how long" in msg:
            reply_text = "Standard shipping takes 2 to 3 business days and is free within the UK. Next-day delivery is available at checkout for orders placed before 2 PM GMT."
        elif "return" in msg or "refund" in msg:
            reply_text = "We offer a 30-day return policy for unused items in their original packaging. Please contact contact@hoverboardstore.co.uk to start your return."
        elif "warranty" in msg:
            reply_text = "Our hoverboards come with a 12-month warranty covering manufacturing faults and technical issues. Physical damage is not covered."
        else:
            reply_text = retrieved_knowledge if retrieved_knowledge else rules_fallback_reply

        return {
            "reply_text": reply_text,
            "intent": intent,
            "confidence": 1.0 if matched_title else 0.7,
            "source_used": matched_title or "General Support Fallback",
            "should_escalate": False,
            "escalation_reason": "",
            "brain_mode": "fallback",
            "route_decision": "answered_by_rules"
        }

    # 4. MiniMax LLM Query execution
    try:
        url = "https://api.minimax.io/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        system_prompt = construct_system_prompt(store_id, retrieved_knowledge or "No knowledge articles found.")
        messages = [{"role": "system", "content": system_prompt}]

        # Include history context if present
        if previous_context:
            for ctx in previous_context:
                role = "assistant" if ctx.get("sender") in ["bot", "agent"] else "user"
                messages.append({"role": role, "content": ctx.get("content", "")})

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=(settings.MINIMAX_CONNECT_TIMEOUT, settings.MINIMAX_READ_TIMEOUT)
        )

        if response.status_code == 200:
            result = response.json()
            reply_text = result["choices"][0]["message"]["content"].strip()

            # Perform a basic validation that LLM did not bypass safety instructions
            safety_lower = reply_text.lower()
            if any(kw in safety_lower for kw in ["smoke", "fire", "spark", "burning"]):
                # Forced transfer if safety words are inside the bot output
                return {
                    "reply_text": "Please stop using the hoverboard immediately. Do not charge it again. If it is safe, unplug it and keep it away from flammable materials. Do not attempt to repair the battery or charger yourself. Our support team has been notified and will reply here shortly. You can also contact contact@hoverboardstore.co.uk.",
                    "intent": intent,
                    "confidence": 0.0,
                    "source_used": "LLM Output Safety Audit Safeguard",
                    "should_escalate": True,
                    "escalation_reason": "LLM output safety audit failed",
                    "brain_mode": "minimax"
                }

            return {
                "reply_text": reply_text,
                "intent": intent,
                "confidence": 0.9,
                "source_used": matched_title or "MiniMax Knowledge Search",
                "should_escalate": False,
                "escalation_reason": "",
                "brain_mode": "minimax",
                "route_decision": "answered_by_minimax"
            }
        else:
            print(f"MiniMax API returned error {response.status_code}: {response.text}")
            raise Exception("Non-200 API response")

    except Exception as e:
        print(f"Error invoking MiniMax API support brain: {e}")
        # Graceful fallback to rules-based logic on LLM failure
        if "stops working" in msg or "not working" in msg or "stopped working" in msg:
            reply_text = "Sorry to hear that. If your hoverboard has stopped working, first make sure it is fully charged and check the charger light. Do not use or charge it if there is any burning smell, smoke, overheating, swelling, water damage, or visible damage. If it still does not work, contact contact@hoverboardstore.co.uk with your order number, a short description of the issue, and photos/videos if safe. Our team can then advise the next step under the 12-month warranty where applicable."
        elif "reset" in msg or "calibrate" in msg or "calibration" in msg:
            reply_text = "If your hoverboard is beeping or flashing red lights, it may need a reset. Turn it off, place it on a flat, level surface, press and hold the power button for 10 seconds until the lights flash, turn it off again, and then turn it back on to calibrate it."
        elif "delivery" in msg or "shipping" in msg or "dispatch" in msg or "how long" in msg:
            reply_text = "Standard shipping takes 2 to 3 business days and is free within the UK. Next-day delivery is available at checkout for orders placed before 2 PM GMT."
        elif "return" in msg or "refund" in msg:
            reply_text = "We offer a 30-day return policy for unused items in their original packaging. Please contact contact@hoverboardstore.co.uk to start your return."
        elif "warranty" in msg:
            reply_text = "Our hoverboards come with a 12-month warranty covering manufacturing faults and technical issues. Physical damage is not covered."
        else:
            reply_text = retrieved_knowledge if retrieved_knowledge else rules_fallback_reply

        return {
            "reply_text": reply_text,
            "intent": intent,
            "confidence": 1.0 if matched_title else 0.7,
            "source_used": matched_title or "General Support Fallback",
            "should_escalate": False,
            "escalation_reason": "",
            "brain_mode": "fallback",
            "route_decision": "answered_by_rules"
        }
