import json
import requests
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from app.config import settings

class Intent(str, Enum):
    shipping_times = "shipping_times"
    return_policy = "return_policy"
    warranty_question = "warranty_question"
    order_tracking = "order_tracking"
    product_recommendation = "product_recommendation"
    age_suitability = "age_suitability"
    product_compatibility = "product_compatibility"
    charging_issue = "charging_issue"
    power_issue = "power_issue"
    reset_calibration = "reset_calibration"
    balance_issue = "balance_issue"
    wheel_motor_issue = "wheel_motor_issue"
    battery_safety = "battery_safety"
    legal_usage = "legal_usage"
    discount_question = "discount_question"
    product_information = "product_information"
    speak_to_human = "speak_to_human"
    general_support = "general_support"
    unknown = "unknown"

class ProductFamily(str, Enum):
    hoverboard = "hoverboard"
    electric_scooter = "electric_scooter"
    hoverkart = "hoverkart"
    hoverboard_bundle = "hoverboard_bundle"
    unknown = "unknown"

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    unknown = "unknown"

class SemanticUnderstanding(BaseModel):
    intent: Intent = Field(default=Intent.unknown, description="Primary intent of the user message")
    sub_intent: Optional[str] = Field(default=None, description="Optional secondary or sub-intent")
    product_entity: Optional[str] = Field(default=None, description="Specific product name or SKU if mentioned")
    product_family: ProductFamily = Field(default=ProductFamily.unknown, description="The product family the user is referring to")
    issue_category: Optional[str] = Field(default=None, description="Broad category of the issue (e.g. power, balance, delivery)")
    risk_level: RiskLevel = Field(default=RiskLevel.low, description="Assessed safety or business risk of the conversation")
    customer_goal: Optional[str] = Field(default=None, description="What the customer ultimately wants to achieve (e.g. refund, fix, advice)")
    age_context: Optional[str] = Field(default=None, description="Age mentioned in the prompt, e.g. '9'")
    order_specific: Optional[bool] = Field(default=False, description="Whether the request is about a specific order")
    needs_clarification: bool = Field(default=False, description="True if the message is too ambiguous and needs clarification")
    clarification_reason: Optional[str] = Field(default=None, description="Reason why clarification is needed if needs_clarification is True")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0 of the classification")

def analyze_semantics(user_message: str, previous_context: Optional[List[Dict[str, str]]] = None) -> SemanticUnderstanding:
    api_key = settings.MINIMAX_API_KEY
    model_name = settings.MINIMAX_MODEL

    default_fallback = SemanticUnderstanding(
        intent=Intent.unknown,
        product_family=ProductFamily.unknown,
        risk_level=RiskLevel.unknown,
        confidence=0.0
    )

    if not api_key or "placeholder" in api_key:
        return default_fallback

    system_prompt = f"""You are a semantic understanding router for a Hoverboard and Electric Scooter store.
Your goal is to classify the user's messy, misspelled, or ambiguous message into structured JSON.
DO NOT answer the user. ONLY output valid JSON matching the exact schema.

Tolerate spelling mistakes (e.g., 'hoverbord' -> hoverboard) and broken english.
Distinguish product families (e.g., 'scooter' -> electric_scooter, 'board' -> hoverboard).
Do not invent facts or map scooter to hoverboard.
If a message is ambiguous (e.g., 'it not work'), set needs_clarification to true.

JSON Schema Requirements:
- intent: Must be one of {[e.value for e in Intent]}
- product_family: Must be one of {[e.value for e in ProductFamily]}
- risk_level: Must be one of {[e.value for e in RiskLevel]}
- confidence: Float between 0.0 and 1.0

Output strictly valid JSON and nothing else."""

    messages = [{"role": "system", "content": system_prompt}]
    
    if previous_context:
        for ctx in previous_context:
            role = "assistant" if ctx.get("sender") in ["bot", "agent"] else "user"
            messages.append({"role": role, "content": ctx.get("content", "")})
            
    messages.append({"role": "user", "content": user_message})

    url = "https://api.minimax.chat/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # We will enforce JSON parsing from the model output.
    # MiniMax supports response_format for structured output in newer models, but we'll instruct it via system prompt to be safe.
    
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5.0)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Clean up markdown code blocks if the model wrapped the JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            parsed = json.loads(content)
            
            return SemanticUnderstanding(
                intent=parsed.get("intent", Intent.unknown),
                sub_intent=parsed.get("sub_intent"),
                product_family=parsed.get("product_family", ProductFamily.unknown),
                issue_category=parsed.get("issue_category"),
                risk_level=parsed.get("risk_level", RiskLevel.low),
                age_context=parsed.get("age_context"),
                needs_clarification=parsed.get("needs_clarification", False),
                confidence=parsed.get("confidence", 0.0)
            )
        else:
            print(f"MiniMax Semantic API Error: {response.status_code} - {response.text}")
            return default_fallback
    except Exception as e:
        print(f"MiniMax Semantic parsing exception: {e}")
        return default_fallback

def build_semantic_metadata(semantic_result: SemanticUnderstanding, classifier_mode: str) -> Dict[str, Any]:
    """
    Serializes a SemanticUnderstanding object into the strictly approved JSONB contract.
    """
    return {
        "semantic_intent": semantic_result.intent.value if hasattr(semantic_result.intent, 'value') else str(semantic_result.intent),
        "semantic_sub_intent": semantic_result.sub_intent,
        "semantic_product_entity": semantic_result.product_entity,
        "semantic_product_family": semantic_result.product_family.value if hasattr(semantic_result.product_family, 'value') else str(semantic_result.product_family),
        "semantic_issue_category": semantic_result.issue_category,
        "semantic_risk_level": semantic_result.risk_level.value if hasattr(semantic_result.risk_level, 'value') else str(semantic_result.risk_level),
        "semantic_customer_goal": semantic_result.customer_goal,
        "semantic_age_context": semantic_result.age_context,
        "semantic_order_specific": semantic_result.order_specific,
        "semantic_needs_clarification": semantic_result.needs_clarification,
        "semantic_clarification_reason": semantic_result.clarification_reason,
        "semantic_confidence": semantic_result.confidence,
        "semantic_classifier_mode": classifier_mode
    }
