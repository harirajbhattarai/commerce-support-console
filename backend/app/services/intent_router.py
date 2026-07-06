import re

def normalize_message(message: str) -> dict:
    """
    Safely normalize customer message to reduce brittleness of exact matching.
    """
    # Original message preserved
    original = message
    
    # Lowercase
    msg = message.lower().strip()
    
    # Apostrophe normalization
    msg = msg.replace("'", "")
    
    # Common punctuation separation (replace with space to keep words distinct)
    msg = re.sub(r'[!?.,;:\-\(\)\[\]"\/]', ' ', msg)
    
    # Collapse repeated whitespace
    msg = re.sub(r'\s+', ' ', msg).strip()
    
    # Conservative repeated character reduction (e.g., pleeease -> please, limiting to 2)
    msg = re.sub(r'(.)\1{2,}', r'\1\1', msg)
    
    # Safe replacements before splitting
    msg = msg.replace("fire red", "red")
    msg = msg.replace("support team", "agent")
    
    # Word families mapping
    word_families = {
        "smoking": "smoke",
        "burning": "burn",
        "burnt": "burn",
        "burned": "burn",
        "smells": "smell",
        "smelling": "smell",
        "smelly": "smell",
        "overheating": "overheat",
        "overheated": "overheat",
        "swelling": "swell",
        "swollen": "swell",
        "advisor": "agent",
        "adviser": "agent",
        "representative": "agent",
        "person": "agent",
        "human": "agent"
    }
    
    # Replace word families (basic token replace)
    tokens = msg.split()
    normalized_tokens = []
    
    for t in tokens:
        if t in word_families:
            normalized_tokens.append(word_families[t])
        else:
            normalized_tokens.append(t)
            
    normalized_message = " ".join(normalized_tokens)
    
    return {
        "original_message": original,
        "normalized_message": normalized_message,
        "normalized_tokens": normalized_tokens
    }

def hard_safety_gate(normalized_data: dict) -> dict:
    """
    Narrow, high-recall pre-LLM safety gate for critical danger scenarios.
    Runs BEFORE retrieval and BEFORE semantic understanding.
    """
    msg = normalized_data["normalized_message"]
    tokens = normalized_data["normalized_tokens"]
    
    matched = False
    matched_concepts = []
    
    # Critical danger concepts (always escalate)
    danger_words = ["smoke", "fire", "spark", "sparks", "burn", "overheat", "melt", "explode", "explosion"]
    for dw in danger_words:
        if dw in tokens:
            matched = True
            matched_concepts.append(dw)
            
    # Contextual danger concepts
    device_context = ["hoverboard", "scooter", "battery", "charger", "device", "board", "it"]
    has_device = any(d in tokens for d in device_context)
    
    # 1. Smell + Device Context
    if "smell" in tokens and has_device:
        matched = True
        matched_concepts.append("smell+device")
        
    # 2. Swell + Battery Context
    if "swell" in tokens and ("battery" in tokens or has_device):
        matched = True
        matched_concepts.append("swell")
        
    # 3. Hot + Battery Context
    if "hot" in tokens and "battery" in tokens:
        matched = True
        matched_concepts.append("hot battery")
        
    if matched:
        return {
            "matched": True,
            "route_decision": "escalated",
            "risk_level": "high",
            "intent": "battery_safety",
            "matched_safety_concepts": matched_concepts,
            "escalation_reason": f"Hard safety gate matched: {', '.join(matched_concepts)}",
            "reply_text": "Please stop using the hoverboard immediately. Do not charge it again. If it is safe, unplug it and keep it away from flammable materials. Do not attempt to repair the battery or charger yourself. Our support team has been notified and will reply here shortly. You can also contact contact@hoverboardstore.co.uk."
        }
        
    return {
        "matched": False
    }

def hard_human_handoff_gate(normalized_data: dict) -> dict:
    """
    Guaranteed human-request gate before MiniMax/retrieval.
    """
    msg = normalized_data["normalized_message"]
    
    matched = False
    matched_concepts = []
    
    # Since variations are normalized to "agent", we look for "agent" requests.
    human_patterns = [
        "need agent", 
        "want talk to agent", 
        "want to talk to agent",
        "speak to agent",
        "speak with agent",
        "talk to agent",
        "talk with agent",
        "talk to a agent",
        "talk to an agent",
        "get me an agent",
        "get me a agent",
        "get me agent",
        "agent please",
        "connect me to agent",
        "transfer me to agent",
        "escalate"
    ]
    
    for pattern in human_patterns:
        if pattern in msg:
            matched = True
            matched_concepts.append(pattern)
            
    if matched:
        return {
            "matched": True,
            "route_decision": "escalated",
            "risk_level": "high",
            "intent": "speak_to_human",
            "matched_human_concepts": matched_concepts,
            "escalation_reason": f"Explicit human request gate matched: {', '.join(matched_concepts)}",
            "reply_text": "Thanks — I’ve passed this to our support team. A team member will reply here shortly."
        }
        
    return {
        "matched": False
    }
